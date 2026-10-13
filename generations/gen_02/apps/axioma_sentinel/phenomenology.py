"""Axioma Sentinel Phenomenological Tool-Being Circuit [L1-G2-006].

Measures the ontological transition from Zuhandenheit (transparent tool-being)
to Vorhandenheit (conspicuous present-at-hand breakdown). Feeds cognitive flow
disruptions directly into Generation 2 feedback loops.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import time

from g2_compiler.phenomenology import PhenomenologicalRuptureEvent, PhenomenologicalToolAuditor


class SentinelPhenomenologyCircuit:
    """Manages the real-time phenomenological telemetry stream for Sentinel."""

    def __init__(self, feedback_json_path: Optional[Path] = None):
        self.auditor = PhenomenologicalToolAuditor(epsilon_flow=0.45, baseline_dwell_seconds=2.0)
        self.feedback_path = feedback_json_path or (
            Path(__file__).parent.parent.parent / "feedback" / "feedback.json"
        )
        self._rupture_history: List[PhenomenologicalRuptureEvent] = []

    def record_interaction(
        self,
        tool_name: str,
        dwell_seconds: float,
        undo_count_in_window: int = 0,
        erratic_input_switches: int = 0,
        unhandled_error_shown: bool = False,
    ) -> PhenomenologicalRuptureEvent:
        """Records an interaction, evaluates Zuhandenheit vs Vorhandenheit, and persists ruptures."""
        event = self.auditor.evaluate_interaction(
            tool_name=tool_name,
            dwell_seconds=dwell_seconds,
            undo_count_in_window=undo_count_in_window,
            erratic_input_switches=erratic_input_switches,
            unhandled_error_shown=unhandled_error_shown,
        )
        self._rupture_history.insert(0, event)

        # If a cognitive flow rupture occurred (tool became Vorhanden), feed to generational feedback!
        if event.phenomenological_state == "VORHANDEN":
            self._feed_rupture_to_feedback(event)

        return event

    def _feed_rupture_to_feedback(self, event: PhenomenologicalRuptureEvent) -> None:
        """Appends the cognitive rupture to generations/gen_02/feedback/feedback.json."""
        if not self.feedback_path.exists():
            return

        try:
            with open(self.feedback_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            active_lessons = data.setdefault("active_g2_lessons", [])
            lesson_record = {
                "lesson_id": f"LES-G2-{len(active_lessons) + 1:03d}",
                "category": "PHENOMENOLOGICAL_FLOW_RUPTURE",
                "severity": "MEDIUM" if event.rupture_index < 0.70 else "HIGH",
                "title": f"Flow Disruption in '{event.tool_name}' ({event.phenomenological_state})",
                "incident_summary": event.cognitive_diagnosis,
                "rupture_index": event.rupture_index,
                "transparency_score": event.transparency_score,
                "timestamp": event.timestamp,
            }
            active_lessons.append(lesson_record)

            with open(self.feedback_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass  # Non-blocking telemetry write

    def get_summary(self) -> Dict[str, Any]:
        """Emits phenomenological status summary for UI and API."""
        avg_transparency = self.auditor.get_average_transparency()
        return {
            "average_transparency_score": round(avg_transparency, 3),
            "current_attunement": "ZUHANDEN (Transparent Extension)" if avg_transparency >= 0.55 else "VORHANDEN (Conspicuous Object)",
            "total_evaluated_events": len(self._rupture_history),
            "ruptures_detected": sum(1 for e in self._rupture_history if e.phenomenological_state == "VORHANDEN"),
            "recent_events": [e.to_dict() for e in self._rupture_history[:10]],
        }
