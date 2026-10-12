"""Adaptive Spaced Repetition System (SRS) Engine based on SM-2.

Computes dynamic review intervals, repetition counts, and ease factor adjustments
based on user feedback ratings (Forgot, Hard, Good, Easy).
"""

from dataclasses import dataclass
import time
from typing import Dict, Any, Tuple


class SrsRating:
    FORGOT = "FORGOT"  # Quality 1
    HARD = "HARD"      # Quality 2
    GOOD = "GOOD"      # Quality 4
    EASY = "EASY"      # Quality 5


class SrsAlgorithm:
    """Implements adaptive SM-2 spaced repetition interval computation."""

    @staticmethod
    def calculate_next_review(word_data: Dict[str, Any], rating: str) -> Dict[str, Any]:
        """Calculates next review schedule given current word state and rating."""
        rep = word_data.get("repetition_level", 0)
        interval = word_data.get("interval_days", 0.0)
        ease = word_data.get("ease_factor", 2.5)
        now = time.time()

        if rating == SrsRating.FORGOT:
            # Resets streak, review due in ~10 minutes (0.007 days)
            new_rep = 0
            new_interval = 0.007
            new_ease = max(1.3, ease - 0.20)
            new_status = "learning"

        elif rating == SrsRating.HARD:
            # Review due soon (1 day or slightly stretched), ease drops
            new_rep = max(1, rep)
            new_interval = max(1.0, interval * 1.2) if rep > 0 else 1.0
            new_ease = max(1.3, ease - 0.15)
            new_status = "learning" if rep < 2 else "review"

        elif rating == SrsRating.GOOD:
            # Standard SM-2 progression
            if rep == 0:
                new_interval = 1.0
            elif rep == 1:
                new_interval = 3.0
            else:
                new_interval = max(3.0, interval * ease)
            new_rep = rep + 1
            new_ease = ease
            new_status = "mastered" if new_rep >= 4 else "review"

        elif rating == SrsRating.EASY:
            # Bonus progression and ease factor boost
            if rep == 0:
                new_interval = 3.0
            elif rep == 1:
                new_interval = 7.0
            else:
                new_interval = max(7.0, interval * ease * 1.3)
            new_rep = rep + 1
            new_ease = min(3.0, ease + 0.15)
            new_status = "mastered" if new_rep >= 3 else "review"

        else:
            raise ValueError(f"Unknown SRS rating: {rating}")

        next_timestamp = now + (new_interval * 86400.0)

        updated = dict(word_data)
        updated["repetition_level"] = new_rep
        updated["interval_days"] = round(new_interval, 3)
        updated["ease_factor"] = round(new_ease, 2)
        updated["next_review"] = next_timestamp
        updated["last_reviewed"] = now
        updated["status"] = new_status

        return updated
