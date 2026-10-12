"""Partitioned Session Store and Puzzle Repository.

Enforces Decoupled Persistence across Boundary 3 ([L1-011_3]) and
Functorial Reversibility ([L1-002]) with optimistic concurrency control.
"""

from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Dict, List, Optional, Tuple

from models import CrosswordGrid, SolverSession


class SessionStore:
    """Manages immutable puzzles and partitioned mutable solver sessions with optimistic locking."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or (Path(__file__).parent.parent / "data")
        self.puzzles_dir = self.base_dir / "puzzles"
        self.sessions_dir = self.base_dir / "sessions"

        self.puzzles_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        self._in_memory_puzzles: Dict[str, CrosswordGrid] = {}
        self._in_memory_sessions: Dict[str, SolverSession] = {}
        self._load_existing_puzzles()

    def _load_existing_puzzles(self) -> None:
        for p_path in self.puzzles_dir.glob("*.json"):
            try:
                with open(p_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    grid = CrosswordGrid.from_dict(data)
                    self._in_memory_puzzles[grid.grid_id] = grid
            except Exception:
                pass

    def save_puzzle(self, grid: CrosswordGrid) -> None:
        self._in_memory_puzzles[grid.grid_id] = grid
        target_path = self.puzzles_dir / f"{grid.grid_id}.json"
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(grid.to_dict(), f, indent=2)

    def get_puzzle(self, puzzle_id: str) -> Optional[CrosswordGrid]:
        return self._in_memory_puzzles.get(puzzle_id)

    def list_puzzles(self) -> List[Dict[str, str]]:
        return [
            {
                "grid_id": g.grid_id,
                "title": g.title,
                "size": f"{g.size_rows}x{g.size_cols}",
                "slots_count": len(g.slots),
            }
            for g in self._in_memory_puzzles.values()
        ]

    def get_or_create_session(
        self, session_id: str, puzzle_id: str, user_id: str = "default_user"
    ) -> SolverSession:
        if session_id in self._in_memory_sessions:
            return self._in_memory_sessions[session_id]

        target_path = self.sessions_dir / f"{session_id}.json"
        if target_path.exists():
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    session = SolverSession.from_dict(data)
                    self._in_memory_sessions[session_id] = session
                    return session
            except Exception:
                pass

        session = SolverSession(
            session_id=session_id,
            puzzle_id=puzzle_id,
            user_id=user_id,
            cells_entered={},
            version=1,
            updated_at=time.time(),
        )
        self._save_session(session)
        return session

    def apply_delta(
        self,
        session_id: str,
        row: int,
        col: int,
        char: str,
        expected_version: Optional[int] = None,
    ) -> Tuple[SolverSession, bool]:
        """Applies a cell mutation with optimistic concurrency control ([L1-002])."""
        session = self._in_memory_sessions.get(session_id)
        if not session:
            raise KeyError(f"Session {session_id} not found")

        # Check optimistic version tag
        if expected_version is not None and expected_version != session.version:
            # Conflict detected: reject or report desync
            return session, False

        key = f"{row},{col}"
        if char:
            session.cells_entered[key] = char.upper()
        else:
            session.cells_entered.pop(key, None)

        session.version += 1
        session.updated_at = time.time()

        # Check completeness
        puzzle = self.get_puzzle(session.puzzle_id)
        if puzzle:
            session.is_complete = self._verify_completeness(session, puzzle)

        self._save_session(session)
        return session, True

    def _verify_completeness(self, session: SolverSession, puzzle: CrosswordGrid) -> bool:
        """Verifies if all fillable cells are entered and match puzzle answers."""
        for slot in puzzle.slots:
            for offset, ch in enumerate(slot.answer):
                if slot.direction == "ACROSS":
                    r = slot.row
                    c = slot.col + offset
                else:
                    r = slot.row + offset
                    c = slot.col
                key = f"{r},{c}"
                entered = session.cells_entered.get(key, "")
                if entered.upper() != ch.upper():
                    return False
        return True

    def _save_session(self, session: SolverSession) -> None:
        self._in_memory_sessions[session.session_id] = session
        target_path = self.sessions_dir / f"{session.session_id}.json"
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception:
            pass


# Global singleton store
GLOBAL_STORE = SessionStore()
