"""Ephemeral Self-Healing Exception Enclaves for Axioma Crossword [L1-G2-002 & L1-016].

Provides bounded multi-pass auto-repair (k <= 3) for corrupted grid schemas,
delta anomalies, and solver bounds, while isolating blast radiuses.
"""

from __future__ import annotations

import logging
import re
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

try:
    from .models import CrosswordGrid, CrypticClue, Direction, WordSlot
except ImportError:
    from models import CrosswordGrid, CrypticClue, Direction, WordSlot

logger = logging.getLogger("AxiomaCrossword.Enclave")


class CrosswordExceptionEnclave:
    """Demarcated Exception Enclave [L1-016] providing blast-radius containment."""

    def __init__(self, enclave_id: str, action: str):
        self.enclave_id = enclave_id
        self.action = action
        self.caught: Optional[str] = None
        self.witness: Optional[Dict[str, Any]] = None

    def __enter__(self) -> CrosswordExceptionEnclave:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            self.caught = str(exc_val)
            self.witness = {
                "enclave_id": self.enclave_id,
                "action": self.action,
                "error_type": exc_type.__name__,
                "error_message": str(exc_val),
                "timestamp": time.time(),
                "blast_radius_isolated": True,
            }
            logger.warning(
                f"[ENCLAVE_TRAP:{self.enclave_id}] Contained {exc_type.__name__}: {exc_val}"
            )
            return True  # Suppress error to isolate blast radius
        return False


class CrosswordHealingEnclave:
    """Ephemeral auto-repair enclave [L1-G2-002] for resilient puzzle & delta persistence."""

    def __init__(self, max_passes: int = 3):
        self.max_passes = max_passes
        self.total_incidents_healed = 0
        self.quarantine_log: List[Dict[str, Any]] = []

    def heal_raw_slot(self, raw_data: Dict[str, Any]) -> Tuple[bool, Optional[WordSlot], List[str]]:
        """Repairs a single malformed WordSlot dict in up to 3 passes."""
        passes_taken: List[str] = []
        data = dict(raw_data)

        # PASS 1: Identifier & Coordinate Coercion
        if not data.get("slot_id"):
            dir_prefix = "A" if str(data.get("direction", "")).upper() == "ACROSS" else "D"
            r = int(data.get("row", 0))
            c = int(data.get("col", 0))
            data["slot_id"] = f"{dir_prefix}_{r}_{c}"
            passes_taken.append("Pass 1: Synthesized missing slot_id from coordinates.")

        try:
            data["direction"] = Direction(str(data.get("direction", "ACROSS")).upper())
        except ValueError:
            data["direction"] = Direction.ACROSS
            passes_taken.append("Pass 1: Coerced invalid direction to ACROSS.")

        data["row"] = max(0, int(data.get("row", 0)))
        data["col"] = max(0, int(data.get("col", 0)))

        # PASS 2: Length and Answer Coherence
        ans = str(data.get("answer", "")).strip().upper()
        clean_ans = re.sub(r"[^A-Z]", "", ans)
        if clean_ans != ans:
            passes_taken.append("Pass 2: Stripped non-alphabetic characters from answer.")
            ans = clean_ans
        data["answer"] = ans

        expected_len = int(data.get("length", len(ans) or 3))
        if len(ans) > 0 and len(ans) != expected_len:
            passes_taken.append(f"Pass 2: Corrected length from {expected_len} to {len(ans)}.")
            data["length"] = len(ans)
        else:
            data["length"] = expected_len

        # PASS 3: Clue Number Invariant Validation
        try:
            num = int(data.get("number", 1))
            data["number"] = max(1, num)
        except (ValueError, TypeError):
            data["number"] = 1
            passes_taken.append("Pass 3: Coerced invalid slot number to 1.")

        try:
            slot = WordSlot(
                slot_id=data["slot_id"],
                direction=data["direction"],
                row=data["row"],
                col=data["col"],
                length=data["length"],
                number=data["number"],
                answer=data["answer"],
            )
            if passes_taken:
                self.total_incidents_healed += 1
            return True, slot, passes_taken
        except Exception as e:
            self.quarantine_log.append({"raw": raw_data, "error": str(e), "timestamp": time.time()})
            return False, None, passes_taken

    def heal_delta_submission(
        self,
        row: int,
        col: int,
        char: str,
        grid_rows: int,
        grid_cols: int,
    ) -> Tuple[bool, int, int, str, List[str]]:
        """Repairs or bounds out-of-bounds user character input."""
        passes_taken = []
        # Clamp coordinates
        clamped_r = max(0, min(grid_rows - 1, int(row)))
        clamped_c = max(0, min(grid_cols - 1, int(col)))
        if clamped_r != row or clamped_c != col:
            passes_taken.append("Pass 1: Clamped out-of-bounds grid coordinates.")

        # Sanitize character input
        clean_ch = str(char).strip().upper()
        if len(clean_ch) > 1:
            clean_ch = clean_ch[0]
            passes_taken.append("Pass 2: Truncated multi-character input to single character.")
        if clean_ch and not clean_ch.isalpha():
            clean_ch = ""
            passes_taken.append("Pass 2: Cleared non-alphabetic character.")

        return True, clamped_r, clamped_c, clean_ch, passes_taken
