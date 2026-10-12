"""Inner Dialogue & Intent FSM (Semantic Progress Machine).
Governs conversational progression, task planning, and tool failure recovery loops.
"""

from enum import Enum
from typing import Any, Dict, Optional, Tuple


class InnerState(str, Enum):
    IDLE = "IDLE"
    INTENT_IDENTIFIED = "INTENT_IDENTIFIED"
    PARAM_ELICITATION = "PARAM_ELICITATION"
    PLAN_PROPOSED = "PLAN_PROPOSED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    ACTION_DISPATCHED = "ACTION_DISPATCHED"
    OUTCOME_EVALUATED = "OUTCOME_EVALUATED"
    RESPONSE_SYNTHESIZED = "RESPONSE_SYNTHESIZED"
    TERMINAL_SUCCESS = "TERMINAL_SUCCESS"
    TERMINAL_FAILED = "TERMINAL_FAILED"
    HALTED = "HALTED"


class InnerFsm:
    """Pure-function deterministic state machine governing conversational semantic flow."""

    def __init__(self, initial_state: InnerState = InnerState.IDLE):
        self.state: InnerState = initial_state
        self.intent: str = ""
        self.params: Dict[str, Any] = {}
        self.active_plan: Optional[str] = None
        self.action_result: Optional[Dict[str, Any]] = None
        self.history: list[InnerState] = [initial_state]

    def transition(self, event: str, payload: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Evaluates transition event. Returns (success, message)."""
        payload = payload or {}
        curr = self.state

        if curr == InnerState.HALTED:
            return False, "Inner FSM is HALTED by Outer Security Governor. Transitions blocked."

        # 1. IDLE -> INTENT_IDENTIFIED
        if curr == InnerState.IDLE and event == "IDENTIFY_INTENT":
            self.intent = payload.get("intent", "general_query")
            self.params = {}
            self.active_plan = None
            self.action_result = None
            self._set_state(InnerState.INTENT_IDENTIFIED)
            return True, f"Intent identified: {self.intent}"

        # 2. INTENT_IDENTIFIED -> PARAM_ELICITATION or PLAN_PROPOSED
        if curr == InnerState.INTENT_IDENTIFIED:
            if event == "REQUIRE_PARAMS":
                self._set_state(InnerState.PARAM_ELICITATION)
                return True, "Parameters required."
            if event == "PROPOSE_PLAN":
                self.params.update(payload.get("params", {}))
                self.active_plan = payload.get("plan", "Standard execution plan")
                self._set_state(InnerState.PLAN_PROPOSED)
                return True, f"Plan proposed: {self.active_plan}"

        # 3. PARAM_ELICITATION -> PLAN_PROPOSED
        if curr == InnerState.PARAM_ELICITATION and event == "PARAMS_PROVIDED":
            self.params.update(payload.get("params", {}))
            self.active_plan = payload.get("plan", "Standard execution plan")
            self._set_state(InnerState.PLAN_PROPOSED)
            return True, f"Parameters provided. Plan proposed: {self.active_plan}"

        # 4. PLAN_PROPOSED -> AWAITING_APPROVAL (Strict Invariant: cannot skip to ACTION_DISPATCHED)
        if curr == InnerState.PLAN_PROPOSED and event == "REQUEST_APPROVAL":
            self._set_state(InnerState.AWAITING_APPROVAL)
            return True, "Awaiting operator approval."

        # Direct skip attempt violation
        if curr in (InnerState.INTENT_IDENTIFIED, InnerState.PLAN_PROPOSED) and event == "DISPATCH_ACTION":
            return False, "INVARIANT VIOLATION: Cannot dispatch action without operator approval."

        # 5. AWAITING_APPROVAL -> ACTION_DISPATCHED
        if curr == InnerState.AWAITING_APPROVAL and event == "APPROVE_ACTION":
            self._set_state(InnerState.ACTION_DISPATCHED)
            return True, "Action approved and dispatched to execution runtime."

        # 6. ACTION_DISPATCHED -> OUTCOME_EVALUATED (Tool Failure Loop Entry)
        if curr == InnerState.ACTION_DISPATCHED and event == "EVALUATE_OUTCOME":
            self.action_result = payload
            self._set_state(InnerState.OUTCOME_EVALUATED)
            return True, "Tool execution complete. Outcome under deterministic evaluation."

        # 7. OUTCOME_EVALUATED: Branching logic for non-deterministic tool outcomes
        if curr == InnerState.OUTCOME_EVALUATED:
            status = payload.get("status") or (self.action_result.get("status") if isinstance(self.action_result, dict) else "SUCCESS")
            
            # Happy path: tool succeeded
            if event == "ACCEPT_OUTCOME":
                self._set_state(InnerState.RESPONSE_SYNTHESIZED)
                return True, "Tool result verified. Response synthesized."

            # Tool Failure Recovery Path A: Transient runtime failure (e.g. 504 / timeout) -> Fallback tool
            if event == "TRIGGER_FALLBACK_PLAN":
                fallback_plan = payload.get("fallback_plan", "Fallback tool selection")
                self.active_plan = fallback_plan
                self._set_state(InnerState.PLAN_PROPOSED)
                return True, f"Transient tool failure handled: routed back to PLAN_PROPOSED ({fallback_plan})"

            # Tool Failure Recovery Path B: Invalid parameters (400 Bad Request) -> Re-elicit params
            if event == "RE_ELICIT_PARAMS":
                self._set_state(InnerState.PARAM_ELICITATION)
                return True, "Tool parameter failure: routed back to PARAM_ELICITATION for correction."

            # Unrecoverable error
            if event == "ABORT":
                self._set_state(InnerState.TERMINAL_FAILED)
                return True, "Unrecoverable tool failure. Dialogue terminated."

        # 8. RESPONSE_SYNTHESIZED -> TERMINAL_SUCCESS
        if curr == InnerState.RESPONSE_SYNTHESIZED and event == "COMPLETE_TURN":
            self._set_state(InnerState.TERMINAL_SUCCESS)
            return True, "Dialogue turn completed successfully."

        # 9. Reset to IDLE
        if curr in (InnerState.TERMINAL_SUCCESS, InnerState.TERMINAL_FAILED) and event == "RESET":
            self._set_state(InnerState.IDLE)
            return True, "Inner FSM reset to IDLE."

        return False, f"Illegal transition from {curr.value} via event '{event}'"

    def force_halt(self, reason: str = "Outer FSM Dominance Rule"):
        """Coupled Halting Morphism (Φ_halt): instantly forces Inner FSM into HALTED."""
        self._set_state(InnerState.HALTED)

    def revert_to_safe(self, target: InnerState = InnerState.IDLE):
        """Functorial Reversibility (L1-002): rollback morphism restoring safe state."""
        self._set_state(target)

    def _set_state(self, new_state: InnerState):
        self.state = new_state
        self.history.append(new_state)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_state": self.state.value,
            "current_intent": self.intent,
            "extracted_params": self.params,
            "active_plan": self.active_plan,
            "action_result": self.action_result,
            "history_depth": len(self.history),
        }
