"""Dynamically Compiled Hierarchical Statechart Engine for: statechart_soc_epistemic_curiosity_engine."""

from typing import Dict, List, Optional


class InvalidStateTransitionError(RuntimeError):
    """Raised when an event is not legal in the active hierarchical state."""
    pass


class GeneratedStatechartMachine:
    """Executes hierarchical XState v5 semantics for statechart_soc_epistemic_curiosity_engine."""

    INITIAL_LEAF_STATE = 'foundational_stratum.mapping_objects_arrows'
    PARENT_MAP: Dict[str, str] = {'root.dialectical_gate': 'root', 'dialectical_gate.conceptual_dead_end': 'root.dialectical_gate', 'dialectical_gate.evaluating_prerequisites': 'root.dialectical_gate', 'dialectical_gate.gate_certified': 'root.dialectical_gate', 'dialectical_gate.socratic_cross_exam': 'root.dialectical_gate', 'root.foundational_stratum': 'root', 'foundational_stratum.dead_end_associativity': 'root.foundational_stratum', 'foundational_stratum.foundational_history': 'root.foundational_stratum', 'foundational_stratum.mapping_objects_arrows': 'root.foundational_stratum', 'foundational_stratum.mastery_of_morphisms': 'root.foundational_stratum', 'foundational_stratum.probing_morphisms': 'root.foundational_stratum', 'root.higher_abstraction_stratum': 'root', 'higher_abstraction_stratum.epistemic_integration_complete': 'root.higher_abstraction_stratum', 'higher_abstraction_stratum.exploring_functors': 'root.higher_abstraction_stratum', 'higher_abstraction_stratum.functor_dead_end': 'root.higher_abstraction_stratum', 'higher_abstraction_stratum.higher_history': 'root.higher_abstraction_stratum', 'higher_abstraction_stratum.natural_transformations': 'root.higher_abstraction_stratum'}
    HISTORY_STATES: List[str] = ['foundational_stratum.foundational_history', 'higher_abstraction_stratum.higher_history']
    TRANSITIONS: Dict[str, Dict[str, str]] = {'dialectical_gate.conceptual_dead_end': {'FUNCTORIAL_UNDO_TO_FOUNDATION': 'foundational_stratum.foundational_history'}, 'dialectical_gate.evaluating_prerequisites': {'PREREQUISITE_REJECTED': 'foundational_stratum.mapping_objects_arrows', 'PREREQUISITE_SATISFIED': 'dialectical_gate.socratic_cross_exam'}, 'dialectical_gate.gate_certified': {'ENTER_EXPLORING_FUNCTORS': 'higher_abstraction_stratum.exploring_functors'}, 'dialectical_gate.socratic_cross_exam': {'CONJECTURE_REFUTED': 'dialectical_gate.conceptual_dead_end', 'ELENCHUS_PASSED': 'dialectical_gate.gate_certified'}, 'foundational_stratum.dead_end_associativity': {'FUNCTORIAL_UNDO_ROLLBACK': 'foundational_stratum.foundational_history'}, 'foundational_stratum.foundational_history': {'RESTORE_DEEP_HISTORY': 'foundational_stratum.probing_morphisms'}, 'foundational_stratum.mapping_objects_arrows': {'PROPOSE_COMPOSITION': 'foundational_stratum.probing_morphisms'}, 'foundational_stratum.mastery_of_morphisms': {'REQUEST_HIGHER_ABSTRACTION': 'dialectical_gate.evaluating_prerequisites'}, 'foundational_stratum.probing_morphisms': {'AXIOM_CONTRADICTION': 'foundational_stratum.dead_end_associativity', 'VERIFY_MORPHISM_LAWS': 'foundational_stratum.mastery_of_morphisms'}, 'higher_abstraction_stratum.exploring_functors': {'IDENTITY_PRESERVATION_BROKEN': 'higher_abstraction_stratum.functor_dead_end', 'VERIFY_FUNCTORIALITY': 'higher_abstraction_stratum.natural_transformations'}, 'higher_abstraction_stratum.functor_dead_end': {'FUNCTORIAL_UNDO_STEP': 'higher_abstraction_stratum.higher_history'}, 'higher_abstraction_stratum.higher_history': {'RESTORE_FUNCTOR_STATE': 'higher_abstraction_stratum.exploring_functors'}, 'higher_abstraction_stratum.natural_transformations': {'CERTIFY_ABSTRACTION': 'higher_abstraction_stratum.epistemic_integration_complete'}}

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
