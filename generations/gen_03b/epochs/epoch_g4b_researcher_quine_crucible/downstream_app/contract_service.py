"""Dynamically Compiled Compositional Contract Service for: contract_g4b_researcher."""

import copy
from typing import Any, Dict, List


class PreConditionViolationError(RuntimeError):
    """Raised when a verb precondition is not satisfied."""
    pass


class PostConditionViolationError(RuntimeError):
    """Raised when a verb postcondition fails to hold after execution."""
    pass


class GeneratedContractService:
    """Executes composed and atomic verbs defined in contract_g4b_researcher."""

    def __init__(self):
        self._undo_stack: List[Dict[str, Any]] = []

    def undo(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """[L1-002] Functorial 1-tap Undo restoring prior state snapshot."""
        if not self._undo_stack:
            return copy.deepcopy(current_state)
        return self._undo_stack.pop()

    def _exec_sub_hypothesis_engine__FormulateSMTHypotheses(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Atomic verb: FormulateSMTHypotheses"""
        if 'islands_seeded' not in state or not (state['islands_seeded'] == True):
            raise PreConditionViolationError(f'Precondition failed in FormulateSMTHypotheses: islands_seeded == True (state={state})')
        state['hypotheses_formulated'] = True
        if not (state.get('hypotheses_formulated') == True):
            raise PostConditionViolationError(f'Postcondition failed in FormulateSMTHypotheses: hypotheses_formulated == True')
        return state

    def _exec_sub_island_isolation__SpawnQuarantinedIslands(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Atomic verb: SpawnQuarantinedIslands"""
        if 'exploratory_token_lease' not in state or not (state['exploratory_token_lease'] >= 60000):
            raise PreConditionViolationError(f'Precondition failed in SpawnQuarantinedIslands: exploratory_token_lease >= 60000 (state={state})')
        state['islands_seeded'] = True
        if not (state.get('islands_seeded') == True):
            raise PostConditionViolationError(f'Postcondition failed in SpawnQuarantinedIslands: islands_seeded == True')
        return state

    def _exec_sub_taboo_filter__FilterTabooDistance(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Atomic verb: FilterTabooDistance"""
        if 'hypotheses_formulated' not in state or not (state['hypotheses_formulated'] == True):
            raise PreConditionViolationError(f'Precondition failed in FilterTabooDistance: hypotheses_formulated == True (state={state})')
        state['taboo_distance_satisfied'] = True
        state['is_certified'] = True
        if not (state.get('taboo_distance_satisfied') == True):
            raise PostConditionViolationError(f'Postcondition failed in FilterTabooDistance: taboo_distance_satisfied == True')
        if not (state.get('is_certified') == True):
            raise PostConditionViolationError(f'Postcondition failed in FilterTabooDistance: is_certified == True')
        return state

    def ComposeEpistemicDiscovery(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Composed parent verb: Executes full discovery across isolated islands and formalizes hypotheses"""
        self._undo_stack.append(copy.deepcopy(state))
        working = copy.deepcopy(state)
        if 'exploratory_token_lease' not in working or not (working['exploratory_token_lease'] >= 60000):
            raise PreConditionViolationError(f'Parent precondition failed in ComposeEpistemicDiscovery: exploratory_token_lease >= 60000')
        working = self._exec_sub_island_isolation__SpawnQuarantinedIslands(working)
        working = self._exec_sub_hypothesis_engine__FormulateSMTHypotheses(working)
        working = self._exec_sub_taboo_filter__FilterTabooDistance(working)
        if not (working.get('is_certified') == True):
            raise PostConditionViolationError(f'Parent postcondition failed in ComposeEpistemicDiscovery: is_certified == True')
        return working
