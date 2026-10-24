"""Dynamically Compiled Hierarchical Statechart Engine for: statechart_byzantine_kinetic_facade."""

from typing import Dict, List, Optional


class InvalidStateTransitionError(RuntimeError):
    """Raised when an event is not legal in the active hierarchical state."""
    pass


class GeneratedStatechartMachine:
    """Executes hierarchical XState v5 semantics for statechart_byzantine_kinetic_facade."""

    INITIAL_LEAF_STATE = 'boot.hw_init'
    PARENT_MAP: Dict[str, str] = {'active': 'facade_system', 'active.adversarial_consensus': 'active', 'adversarial_consensus.commit': 'active.adversarial_consensus', 'adversarial_consensus.pre_prepare': 'active.adversarial_consensus', 'adversarial_consensus.prepare': 'active.adversarial_consensus', 'active.locked_flat_rigid': 'active', 'active.normal_operation': 'active', 'normal_operation.calm_idle': 'active.normal_operation', 'normal_operation.slew_positioning': 'active.normal_operation', 'normal_operation.sun_tracking': 'active.normal_operation', 'active.unwind_recovery': 'active', 'unwind_recovery.calm_sustained_check': 'active.unwind_recovery', 'unwind_recovery.staged_motor_unwind': 'active.unwind_recovery', 'boot': 'facade_system', 'boot.calibration': 'boot', 'boot.hw_init': 'boot', 'boot.neighbor_discovery': 'boot'}
    HISTORY_STATES: List[str] = []
    TRANSITIONS: Dict[str, Dict[str, str]] = {'adversarial_consensus.commit': {'QUORUM_COMMITTED': 'active.locked_flat_rigid'}, 'adversarial_consensus.pre_prepare': {'PROPOSAL_BROADCAST': 'adversarial_consensus.prepare'}, 'adversarial_consensus.prepare': {'QUORUM_PREPARED': 'adversarial_consensus.commit', 'GUST_ABATED': 'normal_operation.sun_tracking'}, 'active.locked_flat_rigid': {'CALM_THRESHOLD_DETECTED': 'unwind_recovery.calm_sustained_check'}, 'normal_operation.calm_idle': {'SUN_MOVED': 'normal_operation.sun_tracking', 'SHEAR_DETECTED': 'adversarial_consensus.pre_prepare'}, 'normal_operation.slew_positioning': {'TARGET_REACHED': 'normal_operation.calm_idle', 'SHEAR_DETECTED': 'adversarial_consensus.pre_prepare'}, 'normal_operation.sun_tracking': {'SOLAR_TICK': 'normal_operation.slew_positioning', 'SHEAR_DETECTED': 'adversarial_consensus.pre_prepare'}, 'unwind_recovery.calm_sustained_check': {'CALM_CONFIRMED_3X': 'unwind_recovery.staged_motor_unwind', 'SHEAR_SPIKE': 'active.locked_flat_rigid'}, 'unwind_recovery.staged_motor_unwind': {'UNWIND_COMPLETE': 'normal_operation.sun_tracking', 'SHEAR_SPIKE': 'active.locked_flat_rigid'}, 'boot.calibration': {'CALIBRATED': 'boot.neighbor_discovery'}, 'boot.hw_init': {'HW_OK': 'boot.calibration'}, 'boot.neighbor_discovery': {'MESH_JOINED': 'normal_operation.sun_tracking'}}

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
