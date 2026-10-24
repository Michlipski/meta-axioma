"""Dynamically Compiled Compositional Contract Service for: contract_soc_system_g3b_facade_quine."""

import copy
from typing import Any, Dict, List


class PreConditionViolationError(RuntimeError):
    """Raised when a verb precondition is not satisfied."""
    pass


class PostConditionViolationError(RuntimeError):
    """Raised when a verb postcondition fails to hold after execution."""
    pass


class GeneratedContractService:
    """Executes composed and atomic verbs defined in contract_soc_system_g3b_facade_quine."""

    def __init__(self):
        self._undo_stack: List[Dict[str, Any]] = []

    def undo(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """[L1-002] Functorial 1-tap Undo restoring prior state snapshot."""
        if not self._undo_stack:
            return copy.deepcopy(current_state)
        return self._undo_stack.pop()

    def _exec_sub_soc_system_g3b_facade_quine_commit__CommitState(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Atomic verb: CommitState"""
        if 'prepared' not in state or not (state['prepared'] == True):
            raise PreConditionViolationError(f'Precondition failed in CommitState: prepared == True (state={state})')
        state['workflow_completed'] = True
        state['state_persisted'] = True
        if not (state.get('workflow_completed') == True):
            raise PostConditionViolationError(f'Postcondition failed in CommitState: workflow_completed == True')
        if not (state.get('state_persisted') == True):
            raise PostConditionViolationError(f'Postcondition failed in CommitState: state_persisted == True')
        return state

    def _exec_sub_soc_system_g3b_facade_quine_validate__ValidateAndPrepare(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Atomic verb: ValidateAndPrepare"""
        if 'input_validated' not in state or not (state['input_validated'] == True):
            raise PreConditionViolationError(f'Precondition failed in ValidateAndPrepare: input_validated == True (state={state})')
        state['prepared'] = True
        if not (state.get('prepared') == True):
            raise PostConditionViolationError(f'Postcondition failed in ValidateAndPrepare: prepared == True')
        return state

    def ExecuteWorkflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Composed parent verb: Primary workflow transition"""
        self._undo_stack.append(copy.deepcopy(state))
        working = copy.deepcopy(state)
        if 'input_validated' not in working or not (working['input_validated'] == True):
            raise PreConditionViolationError(f'Parent precondition failed in ExecuteWorkflow: input_validated == True')
        working = self._exec_sub_soc_system_g3b_facade_quine_validate__ValidateAndPrepare(working)
        working = self._exec_sub_soc_system_g3b_facade_quine_commit__CommitState(working)
        if not (working.get('workflow_completed') == True):
            raise PostConditionViolationError(f'Parent postcondition failed in ExecuteWorkflow: workflow_completed == True')
        if not (working.get('state_persisted') == True):
            raise PostConditionViolationError(f'Parent postcondition failed in ExecuteWorkflow: state_persisted == True')
        return working
