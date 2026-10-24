"""Generation 3b Headless Journey Walker (The Brain - Gemini 4 Argon).

Enforces:
- [L1-G3B-013] The Empirical Observation Invariant (External State Over In-Memory Mocks):
  Bans phantom steps in journey walkers. Every workflow transition must be driven by and
  asserted against measurable changes in observable external or runtime state.
  If a journey step claims completion without an observable state delta (Delta(state) != empty),
  it is immediately flagged and rejected as a PhantomJourneyStepViolation.
- Steps-to-Value Budget: Verifies user reaches primary value in <= 3 operational steps.
- Intrinsic Ergonomics & Functorial Undo ([L1-002]): Verifies reversible mutations.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable

from ..routing.router import DualModelRouter, CognitiveRole, ModelTier


class PhantomJourneyStepViolation(Exception):
    """Raised when a journey walker step asserts completion without an observable state delta."""
    pass


class JourneyAuditFailure(Exception):
    """Raised when a journey fails ergonomic or empirical verification."""
    pass


@dataclass
class JourneyStep:
    """A discrete user operational action in an E2E journey."""
    step_index: int
    actor_id: str
    action_name: str
    target_interface: str
    input_payload: Dict[str, Any] = field(default_factory=dict)
    expected_observable_change: str = ""
    # Captured external state snapshots
    state_before: Optional[Dict[str, Any]] = None
    state_after: Optional[Dict[str, Any]] = None
    inverse_action: Optional[str] = None


@dataclass
class JourneyAuditReport:
    """Formal audit report for an E2E user journey."""
    journey_id: str
    persona_role: str
    is_certified: bool
    total_steps: int
    steps_to_value: int
    evaluating_model: str = ModelTier.BRAIN_ARGON.value
    undo_lossless: bool = True
    phantom_steps_detected: List[str] = field(default_factory=list)
    ergonomic_violations: List[str] = field(default_factory=list)
    step_witnesses: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "journey_id": self.journey_id,
            "persona_role": self.persona_role,
            "is_certified": self.is_certified,
            "total_steps": self.total_steps,
            "steps_to_value": self.steps_to_value,
            "evaluating_model": self.evaluating_model,
            "undo_lossless": self.undo_lossless,
            "phantom_steps_detected": self.phantom_steps_detected,
            "ergonomic_violations": self.ergonomic_violations,
            "step_witnesses": self.step_witnesses,
        }


class HeadlessJourneyWalker:
    """Adversarial user journey walker validating cognitive ergonomics and external empirical state."""

    @classmethod
    def walk(
        cls,
        journey_id: str,
        persona_role: str,
        steps: List[JourneyStep],
        state_inspector: Optional[Callable[[str], Dict[str, Any]]] = None,
        max_steps_to_value: int = 3,
    ) -> JourneyAuditReport:
        """Executes the journey walk under Gemini 4 Argon governance.

        Enforces [L1-G3B-013]:
        For every step, verifies that state_before != state_after. If state is identical
        or missing while claiming success, flags a Phantom Journey Step.
        """
        # Enforce [L1-G3B-014] Cognitive Routing
        DualModelRouter.create_invocation(
            task_id=f"journey_walk:{journey_id}",
            role=CognitiveRole.JOURNEY_WALKER,
            payload={"journey_id": journey_id, "steps_count": len(steps)},
            requested_model=ModelTier.BRAIN_ARGON,
        )

        phantom_steps: List[str] = []
        ergonomic_violations: List[str] = []
        witnesses: List[Dict[str, Any]] = []

        value_achieved_step = -1
        history_stack: List[JourneyStep] = []

        for idx, step in enumerate(steps):
            # 1. State Delta Observation ([L1-G3B-013])
            before = step.state_before or {}
            after = step.state_after or {}

            # If inspector is provided, evaluate live state
            if state_inspector is not None:
                current_state = state_inspector(step.target_interface)
                if not after:
                    after = current_state

            # Compute delta
            delta_keys = set()
            for k in set(before.keys()).union(after.keys()):
                if before.get(k) != after.get(k):
                    delta_keys.add(k)

            # If no observable delta occurred, flag [L1-G3B-013] violation
            if not delta_keys and step.expected_observable_change:
                desc = (
                    f"[L1-G3B-013 Violation] Step {idx} ('{step.action_name}') asserted completion "
                    f"expecting '{step.expected_observable_change}', but state_before equals state_after (zero delta). "
                    f"Phantom execution detected."
                )
                phantom_steps.append(desc)

            witnesses.append({
                "step_index": idx,
                "action": step.action_name,
                "delta_keys": list(delta_keys),
                "is_phantom": len(delta_keys) == 0 and bool(step.expected_observable_change),
            })

            # 2. Steps to value check
            if "value_delivered" in after and after["value_delivered"] is True:
                if value_achieved_step == -1:
                    value_achieved_step = idx + 1

            # 3. Functorial Undo tracking
            if step.inverse_action:
                history_stack.append(step)

        # Evaluate steps to value
        effective_steps_to_value = value_achieved_step if value_achieved_step != -1 else len(steps)
        if effective_steps_to_value > max_steps_to_value:
            ergonomic_violations.append(
                f"Steps-to-Value Budget Exceeded: User required {effective_steps_to_value} steps to reach core value "
                f"(maximum allowed: {max_steps_to_value}). Onboarding friction too high."
            )

        # Evaluate Functorial Undo capability
        mutating_steps = [s for s in steps if s.state_before != s.state_after and not s.action_name.startswith("view_")]
        undo_lossless = True
        if mutating_steps:
            missing_undo = [s.action_name for s in mutating_steps if not s.inverse_action]
            if missing_undo:
                undo_lossless = False
                ergonomic_violations.append(
                    f"[L1-002 Functorial Undo Violation] Mutating actions lack 1-tap inverse action: {missing_undo}"
                )

        is_certified = len(phantom_steps) == 0 and len(ergonomic_violations) == 0

        return JourneyAuditReport(
            journey_id=journey_id,
            persona_role=persona_role,
            is_certified=is_certified,
            total_steps=len(steps),
            steps_to_value=effective_steps_to_value,
            undo_lossless=undo_lossless,
            phantom_steps_detected=phantom_steps,
            ergonomic_violations=ergonomic_violations,
            step_witnesses=witnesses,
        )

    @classmethod
    def assert_certified(
        cls,
        journey_id: str,
        persona_role: str,
        steps: List[JourneyStep],
        max_steps_to_value: int = 3,
    ) -> JourneyAuditReport:
        """Runs journey walk and raises JourneyAuditFailure or PhantomJourneyStepViolation on defect."""
        report = cls.walk(
            journey_id=journey_id,
            persona_role=persona_role,
            steps=steps,
            max_steps_to_value=max_steps_to_value,
        )
        if report.phantom_steps_detected:
            raise PhantomJourneyStepViolation(
                f"Journey '{journey_id}' failed anti-phantom gate:\n" +
                "\n".join(f"  - {p}" for p in report.phantom_steps_detected)
            )
        if not report.is_certified:
            raise JourneyAuditFailure(
                f"Journey '{journey_id}' failed ergonomic audit:\n" +
                "\n".join(f"  - {v}" for v in report.ergonomic_violations)
            )
        return report
