"""Dynamically Compiled Hierarchical Statechart Engine for: statechart_soc_euclidean_canon_studio."""

from typing import Dict, List, Optional


class InvalidStateTransitionError(RuntimeError):
    """Raised when an event is not legal in the active hierarchical state."""
    pass


class GeneratedStatechartMachine:
    """Executes hierarchical XState v5 semantics for statechart_soc_euclidean_canon_studio."""

    INITIAL_LEAF_STATE = 'euclidean_stratum.sculpting_necklaces'
    PARENT_MAP: Dict[str, str] = {'root.contrapuntal_audition_stratum': 'root', 'contrapuntal_audition_stratum.auditing_dyadic_intervals': 'root.contrapuntal_audition_stratum', 'contrapuntal_audition_stratum.auditioning_webaudio_canon': 'root.contrapuntal_audition_stratum', 'contrapuntal_audition_stratum.canon_mastery_complete': 'root.contrapuntal_audition_stratum', 'contrapuntal_audition_stratum.contrapuntal_history': 'root.contrapuntal_audition_stratum', 'contrapuntal_audition_stratum.dead_end_parallel_fifths': 'root.contrapuntal_audition_stratum', 'root.euclidean_stratum': 'root', 'euclidean_stratum.analyzing_toussaint_geometry': 'root.euclidean_stratum', 'euclidean_stratum.dead_end_asymmetric_pulse': 'root.euclidean_stratum', 'euclidean_stratum.euclidean_history': 'root.euclidean_stratum', 'euclidean_stratum.necklace_certified': 'root.euclidean_stratum', 'euclidean_stratum.sculpting_necklaces': 'root.euclidean_stratum', 'root.topological_canon_stratum': 'root', 'topological_canon_stratum.applying_dihedral_functor': 'root.topological_canon_stratum', 'topological_canon_stratum.braiding_voice_trajectories': 'root.topological_canon_stratum', 'topological_canon_stratum.dead_end_non_orientable_tear': 'root.topological_canon_stratum', 'topological_canon_stratum.manifold_glued': 'root.topological_canon_stratum'}
    HISTORY_STATES: List[str] = ['contrapuntal_audition_stratum.contrapuntal_history', 'euclidean_stratum.euclidean_history']
    TRANSITIONS: Dict[str, Dict[str, str]] = {'contrapuntal_audition_stratum.auditing_dyadic_intervals': {'PARALLEL_PERFECTS_DETECTED': 'contrapuntal_audition_stratum.dead_end_parallel_fifths', 'CERTIFY_CONSONANCE_MATRIX': 'contrapuntal_audition_stratum.auditioning_webaudio_canon'}, 'contrapuntal_audition_stratum.auditioning_webaudio_canon': {'SEAL_CANON_SCORE': 'contrapuntal_audition_stratum.canon_mastery_complete'}, 'contrapuntal_audition_stratum.contrapuntal_history': {'RESTORE_CONTRAPUNTAL_STATE': 'contrapuntal_audition_stratum.auditing_dyadic_intervals'}, 'contrapuntal_audition_stratum.dead_end_parallel_fifths': {'SOLVE_OPTIMAL_ROTATION_RHO': 'contrapuntal_audition_stratum.contrapuntal_history'}, 'euclidean_stratum.analyzing_toussaint_geometry': {'GEOMETRY_DEGENERATE': 'euclidean_stratum.dead_end_asymmetric_pulse', 'VERIFY_MAXIMAL_EVENNESS': 'euclidean_stratum.necklace_certified'}, 'euclidean_stratum.dead_end_asymmetric_pulse': {'FUNCTORIAL_UNDO_GEOMETRY': 'euclidean_stratum.euclidean_history'}, 'euclidean_stratum.euclidean_history': {'RESTORE_EUCLIDEAN_HISTORY': 'euclidean_stratum.analyzing_toussaint_geometry'}, 'euclidean_stratum.necklace_certified': {'FOLD_CANON_MANIFOLD': 'topological_canon_stratum.applying_dihedral_functor'}, 'euclidean_stratum.sculpting_necklaces': {'INSCRIBE_POLYGON': 'euclidean_stratum.analyzing_toussaint_geometry'}, 'topological_canon_stratum.applying_dihedral_functor': {'COMPUTE_CRAB_OR_MOEBIUS': 'topological_canon_stratum.braiding_voice_trajectories', 'OPERATOR_INVALID': 'euclidean_stratum.sculpting_necklaces'}, 'topological_canon_stratum.braiding_voice_trajectories': {'INVOLUTION_DRIFT_DETECTED': 'topological_canon_stratum.dead_end_non_orientable_tear', 'VERIFY_BRAID_CLOSURE': 'topological_canon_stratum.manifold_glued'}, 'topological_canon_stratum.dead_end_non_orientable_tear': {'FUNCTORIAL_UNDO_TOPOLOGY': 'euclidean_stratum.euclidean_history'}, 'topological_canon_stratum.manifold_glued': {'ENTER_CONTRAPUNTAL_AUDIT': 'contrapuntal_audition_stratum.auditing_dyadic_intervals'}}

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
