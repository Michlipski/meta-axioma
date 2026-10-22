"""Universal Usability & Cognitive Ergonomics Heuristics Catalog and Audit Engine for System G2b.

Formalizes Nielsen-Norman 10 Usability Heuristics, Fitts's Law, Hick's Law, and Miller's Law
into auditable pre-synthesis predicates evaluated across Semantic IR, Statechart IR, and emitted ASTs.
"""

import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple

from g2b_compiler.matrix.models import Tier2UsabilityHeuristic


# Universal Ergonomics Catalog
UNIVERSAL_USABILITY_HEURISTICS: Dict[str, Tier2UsabilityHeuristic] = {
    # Nielsen Norman 10 Usability Heuristics
    "HEUR-UX-001": Tier2UsabilityHeuristic(
        heuristic_id="HEUR-UX-001",
        name="Visibility of System Status",
        category="nielsen_norman",
        description="Every asynchronous operation (network, persistence, synthesis) MUST have an explicit loading/progress state with visual indicators.",
        audit_rule="For all async actions A: StateNode(A) must have dedicated loading substate or progress event."
    ),
    "HEUR-UX-002": Tier2UsabilityHeuristic(
        heuristic_id="HEUR-UX-002",
        name="Match Between System & Real World",
        category="nielsen_norman",
        description="System vocabulary and concepts must mirror natural human domain language without raw developer jargon.",
        audit_rule="Identifiers presented to users must pass natural language dictionary check; forbidden words: [stale, chunk, pointer, null, fsm]."
    ),
    "HEUR-UX-003": Tier2UsabilityHeuristic(
        heuristic_id="HEUR-UX-003",
        name="User Control & Freedom",
        category="nielsen_norman",
        description="Every compound state must have an explicit emergency exit (CANCEL/ABORT), and non-terminal mutations must provide universal 1-tap Undo (Cmd+Z).",
        audit_rule="Every non-root compound state must accept ABORT/CANCEL or BACK. Undo capability must be declared in capabilities."
    ),
    "HEUR-UX-004": Tier2UsabilityHeuristic(
        heuristic_id="HEUR-UX-004",
        name="Consistency & Standards",
        category="nielsen_norman",
        description="Platform conventions must be honored: dark/light theme tokens, standard keyboard shortcuts (Space to flip, 1-4 to rate), semantic HTML.",
        audit_rule="Design tokens must provide high-contrast text and standard interactive keybindings."
    ),
    "HEUR-UX-005": Tier2UsabilityHeuristic(
        heuristic_id="HEUR-UX-005",
        name="Error Prevention",
        category="nielsen_norman",
        description="Destructive actions (e.g. deleting cards, resetting decks) require confirmation gates or non-destructive undo.",
        audit_rule="Any DELETE or RESET event must have a preceding confirmation prompt state or automatic undo snapshot."
    ),
    "HEUR-UX-006": Tier2UsabilityHeuristic(
        heuristic_id="HEUR-UX-006",
        name="Recognition Rather than Recall",
        category="nielsen_norman",
        description="Instructions and cues must be visible in context (e.g. keybind hints on buttons, card flip prompts, inline phonetic guides).",
        audit_rule="Input fields and flashcard prompts must provide placeholder hints and visual affordances."
    ),
    "HEUR-UX-007": Tier2UsabilityHeuristic(
        heuristic_id="HEUR-UX-007",
        name="Flexibility & Efficiency of Use",
        category="nielsen_norman",
        description="Support both touch interaction for novice mobile and keyboard accelerators for power users.",
        audit_rule="Primary value actions must bind both pointer click and keyboard shortcuts."
    ),
    "HEUR-UX-008": Tier2UsabilityHeuristic(
        heuristic_id="HEUR-UX-008",
        name="Aesthetic & Minimalist Design",
        category="nielsen_norman",
        description="Eliminate irrelevant dialogs. Respect visual dignity: clear typographic hierarchy, generous padding, zero cluttered borders.",
        audit_rule="Layouts must enforce clean spacing, responsive typography, and uncluttered views."
    ),
    "HEUR-UX-009": Tier2UsabilityHeuristic(
        heuristic_id="HEUR-UX-009",
        name="Help Users Recognize & Recover from Errors",
        category="nielsen_norman",
        description="Error states must provide plain language explanations and 1-click recovery actions (e.g. Retry, Offline Mode).",
        audit_rule="Every error stateNode must define a transition back to a non-error state."
    ),
    "HEUR-UX-010": Tier2UsabilityHeuristic(
        heuristic_id="HEUR-UX-010",
        name="Calm Technology & Notification Hygiene",
        category="calm_tech",
        description="Notifications must be strictly opt-in, non-modal, frequency-capped, and dispatch only when actionable value exists.",
        audit_rule="Notification capability must require opt-in permission and throttle to <= 1 alert per day."
    ),

    # Psychophysical Interaction Laws
    "HEUR-COG-001": Tier2UsabilityHeuristic(
        heuristic_id="HEUR-COG-001",
        name="Fitts's Law Touch Target Baseline",
        category="psychophysical",
        description="Interactive touch targets must measure at least 44x44px with comfortable inter-target margins.",
        audit_rule="Button and interactive element min-height must be >= 44px."
    ),
    "HEUR-COG-002": Tier2UsabilityHeuristic(
        heuristic_id="HEUR-COG-002",
        name="Hick's Law Decision Density Limiter",
        category="psychophysical",
        description="Micro-session choices and menu options must be bounded (e.g. review queues capped at 3-15 cards; menus <= 5 options).",
        audit_rule="Session batch size must be capped at <= 15 items per active queue."
    ),
    "HEUR-COG-003": Tier2UsabilityHeuristic(
        heuristic_id="HEUR-COG-003",
        name="Miller's Working Memory Limit",
        category="psychophysical",
        description="Displayed information density per view panel must not exceed 7 +/- 2 discrete conceptual chunks.",
        audit_rule="Active dashboard and review panels must present <= 9 visual content modules."
    )
}


class UsabilityHeuristicAuditor:
    """Audits specifications and emitted assets against the Universal Ergonomics Catalog."""

    def __init__(self):
        self.heuristics = UNIVERSAL_USABILITY_HEURISTICS

    def generate_component_hash(self, component_name: str, code_snippet: str) -> str:
        """Computes a deterministic hash for tracking stateful human overrides."""
        norm = f"{component_name}::{code_snippet.strip()}".encode("utf-8")
        return hashlib.sha256(norm).hexdigest()[:16]

    def audit_statechart_usability(self, statechart_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Audits an XState v5 statechart for UX heuristics (visibility, control, error recovery)."""
        violations = []
        states = statechart_dict.get("states", {})

        # 1. HEUR-UX-003: Check compound states for emergency exits (CANCEL / ABORT / BACK)
        for state_name, state_node in states.items():
            substates = state_node.get("states", {})
            if substates:
                transitions = state_node.get("on", {})
                has_exit = any(evt in transitions for evt in ["CANCEL", "ABORT", "BACK", "CLOSE", "EXIT", "CLOSE_SESSION", "EXIT_REVIEW", "EXIT_CRAM"])
                # Also check substate exits
                sub_has_exit = any(
                    any(evt in sub.get("on", {}) for evt in ["CANCEL", "ABORT", "BACK", "CLOSE", "EXIT", "CLOSE_SESSION", "EXIT_REVIEW", "EXIT_CRAM"])
                    for sub in substates.values()
                )
                if not (has_exit or sub_has_exit):
                    violations.append({
                        "heuristic_id": "HEUR-UX-003",
                        "component_name": f"state.{state_name}",
                        "component_hash": self.generate_component_hash(state_name, json.dumps(state_node)),
                        "message": f"Compound state '{state_name}' lacks an explicit emergency exit (CANCEL/ABORT/BACK)."
                    })

        # 2. HEUR-UX-009: Check error states for recovery paths
        for state_name, state_node in states.items():
            is_error = state_node.get("meta", {}).get("is_error_state", False) or "error" in state_name.lower() or "fallback" in state_name.lower()
            if is_error:
                on_trans = state_node.get("on", {})
                if not on_trans:
                    violations.append({
                        "heuristic_id": "HEUR-UX-009",
                        "component_name": f"state.{state_name}",
                        "component_hash": self.generate_component_hash(state_name, json.dumps(state_node)),
                        "message": f"Error state '{state_name}' is a dead end without recovery transitions."
                    })
            # Check substates
            for sub_name, sub_node in state_node.get("states", {}).items():
                sub_error = sub_node.get("meta", {}).get("is_error_state", False) or "error" in sub_name.lower() or "fallback" in sub_name.lower()
                if sub_error and not sub_node.get("on", {}):
                    violations.append({
                        "heuristic_id": "HEUR-UX-009",
                        "component_name": f"state.{state_name}.{sub_name}",
                        "component_hash": self.generate_component_hash(f"{state_name}.{sub_name}", json.dumps(sub_node)),
                        "message": f"Error substate '{state_name}.{sub_name}' has zero recovery transitions."
                    })

        return violations

    def audit_css_ergonomics(self, css_content: str) -> List[Dict[str, Any]]:
        """Audits stylesheet for Fitts's Law touch targets (>=44px)."""
        import re
        violations = []
        # Check touch target variable or button min-height
        match = re.search(r"--touch-target:\s*(\d+)px", css_content)
        if match:
            val = int(match.group(1))
            if val < 44:
                violations.append({
                    "heuristic_id": "HEUR-COG-001",
                    "component_name": "css.--touch-target",
                    "component_hash": self.generate_component_hash("css.--touch-target", match.group(0)),
                    "message": f"Fitts's Law Violation: Touch target is {val}px, which is below the mandatory 44px ergonomic baseline."
                })
        elif "min-height: 44px" not in css_content and ".btn" in css_content:
            violations.append({
                "heuristic_id": "HEUR-COG-001",
                "component_name": "css.button_targets",
                "component_hash": self.generate_component_hash("css.button_targets", "min-height"),
                "message": "Fitts's Law Warning: Button classes do not explicitly declare >=44px minimum touch target."
            })

        return violations
