"""Phenomenological Tool-Being & Zuhandenheit Attunement Invariant [L1-G2-006].

Exogenous Domain: Heideggerian Phenomenological Ontology & Tool-Being.
Philosophy:
    A tool is "ready-to-hand" (Zuhandenheit) when it acts as an invisible,
    seamless extension of human intent; the human looks *through* the tool at the world.
    It becomes "present-at-hand" (Vorhandenheit) when it breaks, lags, or stutters,
    forcing the human to look *at* the tool as an alien, cumbersome object.

Mathematical Formalization:
    Intentional Transparency: Ψ_tool(t) ∈ [0, 1]
    Flow Dwell Time: τ_dwell vs Expected Velocity τ_flow
    Rupture Index:
        R_rupture = |dΨ_tool / dt| · Θ(τ_dwell - τ_flow) + (UndoClusteringWeight · C_undo)
    When R_rupture > ε_flow, the system flags a "conspicuousness rupture" and triggers
    ephemeral ambient recovery before the human experiences conscious alienation.
"""

from typing import Any, Dict, List, Optional
import math
import time

from g2_compiler.types import PersonaModel


class PhenomenologicalRuptureEvent:
    """Telemetry record capturing the exact moment tool transparency breaks."""

    def __init__(
        self,
        event_id: str,
        timestamp: float,
        tool_name: str,
        transparency_score: float,
        rupture_index: float,
        hesitation_seconds: float,
        undo_cluster_count: int,
        focus_target: str,  # 'WORLD_TASK' (Zuhanden) vs 'TOOL_MECHANISM' (Vorhanden)
        phenomenological_state: str,  # 'ZUHANDEN' (ready-to-hand) vs 'VORHANDEN' (present-at-hand)
        cognitive_diagnosis: str,
    ):
        self.event_id = event_id
        self.timestamp = timestamp
        self.tool_name = tool_name
        self.transparency_score = transparency_score
        self.rupture_index = rupture_index
        self.hesitation_seconds = hesitation_seconds
        self.undo_cluster_count = undo_cluster_count
        self.focus_target = focus_target
        self.phenomenological_state = phenomenological_state
        self.cognitive_diagnosis = cognitive_diagnosis

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "tool_name": self.tool_name,
            "transparency_score": self.transparency_score,
            "rupture_index": self.rupture_index,
            "hesitation_seconds": self.hesitation_seconds,
            "undo_cluster_count": self.undo_cluster_count,
            "focus_target": self.focus_target,
            "phenomenological_state": self.phenomenological_state,
            "cognitive_diagnosis": self.cognitive_diagnosis,
        }


class PhenomenologicalToolAuditor:
    """Measures the ontological transparency (Zuhandenheit vs Vorhandenheit) of tool interactions."""

    def __init__(self, epsilon_flow: float = 0.45, baseline_dwell_seconds: float = 2.0):
        self.epsilon_flow = epsilon_flow
        self.baseline_dwell_seconds = baseline_dwell_seconds
        self._interaction_history: List[Dict[str, Any]] = []

    def evaluate_interaction(
        self,
        tool_name: str,
        dwell_seconds: float,
        undo_count_in_window: int,
        erratic_input_switches: int,
        unhandled_error_shown: bool,
    ) -> PhenomenologicalRuptureEvent:
        """Computes the ontological transparency and detects whether the tool became present-at-hand."""
        now = time.time()
        event_id = f"rup_{int(now * 1000)}"

        # 1. Hesitation factor: excess dwell beyond natural cognitive flow
        hesitation = max(0.0, dwell_seconds - self.baseline_dwell_seconds)
        hesitation_ratio = hesitation / max(self.baseline_dwell_seconds, 1.0)

        # 2. Undo clustering factor: rapid undos indicate intention mismatch
        undo_penalty = min(undo_count_in_window * 0.35, 1.0)

        # 3. Mode thrashing: switching rapidly between menus indicates loss of transparency
        thrashing_penalty = min(erratic_input_switches * 0.20, 0.60)

        # 4. Error obstacle: encountering an unhandled error forces direct visual focus on the tool
        error_penalty = 0.50 if unhandled_error_shown else 0.0

        # Calculate Rupture Index R_rupture
        rupture_index = min(
            1.0,
            (hesitation_ratio * 0.30) + undo_penalty + thrashing_penalty + error_penalty
        )

        # Ontological Transparency Ψ_tool = 1.0 - R_rupture
        transparency = max(0.0, 1.0 - rupture_index)

        # Classify Heideggerian State
        if rupture_index >= self.epsilon_flow:
            state = "VORHANDEN"  # Present-at-hand (cumbersome object, broken flow)
            focus = "TOOL_MECHANISM"
            if unhandled_error_shown:
                diagnosis = "Conspicuous breakdown: opaque error forced user to look AT tool."
            elif undo_count_in_window >= 2:
                diagnosis = "Obstinacy: repetitive undo loop indicates mismatch between user intent and tool effect."
            else:
                diagnosis = "Obtrusiveness: user dwell and input thrashing reveal cognitive flow stagnation."
        else:
            state = "ZUHANDEN"  # Ready-to-hand (transparent extension of will)
            focus = "WORLD_TASK"
            diagnosis = "Transparent extension: human operates unhindered through the tool onto the objective."

        event = PhenomenologicalRuptureEvent(
            event_id=event_id,
            timestamp=now,
            tool_name=tool_name,
            transparency_score=transparency,
            rupture_index=rupture_index,
            hesitation_seconds=hesitation,
            undo_cluster_count=undo_count_in_window,
            focus_target=focus,
            phenomenological_state=state,
            cognitive_diagnosis=diagnosis,
        )
        self._interaction_history.append(event.to_dict())
        return event

    def get_average_transparency(self) -> float:
        """Returns moving average of tool transparency Ψ_tool."""
        if not self._interaction_history:
            return 1.0
        return sum(e["transparency_score"] for e in self._interaction_history) / len(self._interaction_history)
