"""Phenomenological Tool-Being & Zuhandenheit Telemetry for Axioma Crossword [L1-G2-006].

Measures the ontological transition of the Crossword Studio between:
- ZUHANDEN (Ready-to-hand): The puzzle interface recedes into transparent, joyful contemplation.
- VORHANDEN (Present-at-hand): Frictions (awkward clues, sluggish keys) force user to stare AT the tool.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class CrosswordPhenomenologyTracker:
    """Tracks solver flow attunement and conspicuous ruptures."""

    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or Path(__file__).parent / "data" / "phenomenology.json"
        self._keystroke_timestamps: List[float] = []
        self._ruptures_logged = 0
        self._inspection_count = 0
        self._feedback_count = 0

    def record_keystroke(self) -> None:
        """Records user keystroke for fluidity velocity analysis."""
        now = time.time()
        self._keystroke_timestamps.append(now)
        # Keep sliding window of last 100 keystrokes
        if len(self._keystroke_timestamps) > 100:
            self._keystroke_timestamps.pop(0)

    def record_clue_inspection(self) -> None:
        """Records clue anatomy breakdown view."""
        self._inspection_count += 1

    def record_friction_rupture(self, reason: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Logs a phenomenological breakdown (Vorhandenheit)."""
        self._ruptures_logged += 1
        entry = {
            "timestamp": time.time(),
            "reason": reason,
            "details": details or {},
            "rupture_id": f"rup_cw_{self._ruptures_logged}",
        }
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            existing = []
            if self.log_path.exists():
                with open(self.log_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            existing.append(entry)
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump(existing[-50:], f, indent=2)
        except Exception:
            pass

    def compute_transparency_score(self) -> float:
        """Calculates current Zuhandenheit transparency score in [0.0..1.0]."""
        # Baseline score starts high
        score = 0.95
        # Deduct for ruptures
        score -= min(0.50, self._ruptures_logged * 0.05)
        # Reward active typing fluidity
        if len(self._keystroke_timestamps) >= 5:
            intervals = [
                self._keystroke_timestamps[i] - self._keystroke_timestamps[i - 1]
                for i in range(1, len(self._keystroke_timestamps))
            ]
            avg_interval = sum(intervals) / len(intervals)
            # Fluid solving pace is between 0.3s and 1.5s per letter
            if 0.2 <= avg_interval <= 2.0:
                score += 0.05
        return max(0.0, min(1.0, round(score, 3)))

    def get_telemetry_snapshot(self) -> Dict[str, Any]:
        return {
            "transparency_score": self.compute_transparency_score(),
            "tool_state": "ZUHANDEN" if self.compute_transparency_score() >= 0.70 else "VORHANDEN",
            "keystrokes_tracked": len(self._keystroke_timestamps),
            "clue_inspections": self._inspection_count,
            "ruptures_logged": self._ruptures_logged,
        }
