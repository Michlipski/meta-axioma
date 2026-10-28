"""Dynamically Compiled Hierarchical Statechart Engine for: statechart_g4b_researcher."""

from typing import Dict, List, Optional


class InvalidStateTransitionError(RuntimeError):
    """Raised when an event is not legal in the active hierarchical state."""
    pass


class GeneratedStatechartMachine:
    """Executes hierarchical XState v5 semantics for statechart_g4b_researcher."""

    INITIAL_LEAF_STATE = 'boot.sovereign_init'
    PARENT_MAP: Dict[str, str] = {'active': 'researcher_system', 'active.adversarial_crucible': 'active', 'boundary_stress_fuzzing': 'active.adversarial_crucible', 'crucible_certified': 'active.adversarial_crucible', 'crucible_deep_history': 'active.adversarial_crucible', 'dialectical_negation_inject': 'active.adversarial_crucible', 'mode_collapse_enclave': 'active.adversarial_crucible', 'novelty_search_active': 'active.adversarial_crucible', 'pareto_frontier_filter': 'active.adversarial_crucible', 'taboo_distance_check': 'active.adversarial_crucible', 'active.epistemic_discovery': 'active', 'anti_shortcut_enclave': 'active.epistemic_discovery', 'constraint_boundary_mapping': 'active.epistemic_discovery', 'discovery_deep_history': 'active.epistemic_discovery', 'discovery_evaluating': 'active.epistemic_discovery', 'hypothesis_formulation': 'active.epistemic_discovery', 'island_quarantine': 'active.epistemic_discovery', 'active.parallel_fuzzer': 'active', 'fuzzer_evaluating_response': 'active.parallel_fuzzer', 'fuzzer_fault_trapped': 'active.parallel_fuzzer', 'fuzzer_generating_vectors': 'active.parallel_fuzzer', 'fuzzer_quiescent': 'active.parallel_fuzzer', 'active.parallel_meter': 'active', 'meter_bit_erasure_sample': 'active.parallel_meter', 'meter_capital_rebalance': 'active.parallel_meter', 'meter_cutoff_tripped': 'active.parallel_meter', 'meter_monitoring': 'active.parallel_meter', 'active.protocol_adjudication': 'active', 'adjudication_deep_history': 'active.protocol_adjudication', 'builder_rfc_ingress': 'active.protocol_adjudication', 'generational_handover_ready': 'active.protocol_adjudication', 'rfc_counter_proof_enclave': 'active.protocol_adjudication', 'rfc_counter_proof_eval': 'active.protocol_adjudication', 'spec_amendment_signed': 'active.protocol_adjudication', 'spec_bundle_published': 'active.protocol_adjudication', 'boot': 'researcher_system', 'boot.quarantine_setup': 'boot', 'boot.sovereign_init': 'boot', 'epistemic_zenith_sealed': 'researcher_system', 'unwind_recovery_enclave': 'researcher_system'}
    HISTORY_STATES: List[str] = ['adjudication_deep_history', 'crucible_deep_history', 'discovery_deep_history']
    TRANSITIONS: Dict[str, Dict[str, str]] = {'boundary_stress_fuzzing': {'EV_STRESS_PASSED': 'pareto_frontier_filter'}, 'crucible_certified': {'EV_EMIT_DELIVERABLES': 'spec_bundle_published'}, 'crucible_deep_history': {'EV_RESTORE_CRUCIBLE': 'novelty_search_active'}, 'dialectical_negation_inject': {'EV_NEGATION_APPLIED': 'boundary_stress_fuzzing'}, 'mode_collapse_enclave': {'EV_FORCE_NEGATION': 'dialectical_negation_inject'}, 'novelty_search_active': {'EV_EVALUATE_NOVELTY': 'taboo_distance_check'}, 'pareto_frontier_filter': {'EV_CHECKPOINT_CRUCIBLE': 'crucible_deep_history', 'EV_PARETO_OPTIMAL': 'crucible_certified'}, 'taboo_distance_check': {'EV_TABOO_BREACH': 'mode_collapse_enclave', 'EV_TABOO_SATISFIED': 'dialectical_negation_inject'}, 'anti_shortcut_enclave': {'EV_UNWIND_SHORTCUT': 'hypothesis_formulation'}, 'constraint_boundary_mapping': {'EV_BOUNDARIES_MAPPED': 'discovery_evaluating'}, 'discovery_deep_history': {'EV_RESTORE_DISCOVERY': 'hypothesis_formulation'}, 'discovery_evaluating': {'EV_SHORTCUT_DETECTED': 'anti_shortcut_enclave', 'EV_CHECKPOINT_DISCOVERY': 'discovery_deep_history', 'EV_START_FUZZER': 'fuzzer_quiescent', 'EV_START_METER': 'meter_monitoring', 'EV_DISCOVERY_CERTIFIED': 'novelty_search_active'}, 'hypothesis_formulation': {'EV_HYPOTHESIS_FORMULATED': 'constraint_boundary_mapping'}, 'island_quarantine': {'EV_ISLANDS_SEEDED': 'hypothesis_formulation'}, 'fuzzer_evaluating_response': {'EV_FAULT_TRAPPED': 'fuzzer_fault_trapped'}, 'fuzzer_fault_trapped': {'EV_FAULT_LOGGED': 'island_quarantine'}, 'fuzzer_generating_vectors': {'EV_VECTORS_DISPATCHED': 'fuzzer_evaluating_response'}, 'fuzzer_quiescent': {'EV_FUZZ_TICK': 'fuzzer_generating_vectors'}, 'meter_bit_erasure_sample': {'EV_REBALANCE_CAPITAL': 'meter_capital_rebalance'}, 'meter_capital_rebalance': {'EV_BUDGET_EXHAUSTED': 'meter_cutoff_tripped', 'EV_CONTINUE_MONITORING': 'island_quarantine'}, 'meter_cutoff_tripped': {'EV_RETRY_METER': 'island_quarantine'}, 'meter_monitoring': {'EV_BIT_ERASURE_EVENT': 'meter_bit_erasure_sample'}, 'adjudication_deep_history': {'EV_RESTORE_ADJUDICATION': 'spec_bundle_published'}, 'builder_rfc_ingress': {'EV_SUBMIT_RFC': 'rfc_counter_proof_eval'}, 'generational_handover_ready': {'EV_TRIGGER_GLOBAL_UNWIND': 'unwind_recovery_enclave', 'EV_SEAL_CRUCIBLE': 'epistemic_zenith_sealed'}, 'rfc_counter_proof_enclave': {'EV_REJECT_RFC_WITH_PROOF': 'builder_rfc_ingress'}, 'rfc_counter_proof_eval': {'EV_AXIOM_VIOLATION': 'rfc_counter_proof_enclave', 'EV_AMENDMENT_PROVED': 'spec_amendment_signed'}, 'spec_amendment_signed': {'EV_CHECKPOINT_ADJUDICATION': 'adjudication_deep_history', 'EV_ALL_RFCS_RESOLVED': 'generational_handover_ready'}, 'spec_bundle_published': {'EV_BUILDER_ATTACHED': 'builder_rfc_ingress'}, 'boot.quarantine_setup': {'EV_BOOT_READY': 'island_quarantine'}, 'boot.sovereign_init': {'EV_BOOT_POST': 'boot.quarantine_setup'}, 'unwind_recovery_enclave': {'EV_UNWIND_COMPLETE': 'generational_handover_ready'}}

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
