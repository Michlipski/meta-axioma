"""Domain types and data representations for Axioma Crossword Engine.

Conforms to [trace/domains/app_specification.domain.md] and embodies
L1-004 (Universal Grammar Clue AST), L1-015_1 (Compositional Boundary Isolation),
and L1-008 (Landauer Thermodynamic Search Accounting).
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class Direction(str, Enum):
    ACROSS = "ACROSS"
    DOWN = "DOWN"


class ClueType(str, Enum):
    ANAGRAM = "ANAGRAM"
    HIDDEN_WORD = "HIDDEN_WORD"
    CONTAINER = "CONTAINER"
    CHARADE = "CHARADE"
    REVERSAL = "REVERSAL"
    DOUBLE_DEF = "DOUBLE_DEF"
    HOMOPHONE = "HOMOPHONE"


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


@dataclass(frozen=True)
class WordSlot:
    slot_id: str
    direction: Direction
    row: int
    col: int
    length: int
    number: int
    answer: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slot_id": self.slot_id,
            "direction": self.direction.value,
            "row": self.row,
            "col": self.col,
            "length": self.length,
            "number": self.number,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WordSlot:
        return cls(
            slot_id=data["slot_id"],
            direction=Direction(data["direction"]),
            row=data["row"],
            col=data["col"],
            length=data["length"],
            number=data["number"],
            answer=data.get("answer", ""),
        )


@dataclass(frozen=True)
class CrypticClue:
    """Universal Grammar representation of a cryptic clue AST ([L1-004])."""
    clue_id: str
    slot_id: str
    number: int
    direction: Direction
    surface_text: str
    length: int
    answer: str
    definition: str
    clue_type: ClueType
    indicator: str = ""
    fodder: str = ""
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clue_id": self.clue_id,
            "slot_id": self.slot_id,
            "number": self.number,
            "direction": self.direction.value,
            "surface_text": self.surface_text,
            "length": self.length,
            "answer": self.answer,
            "definition": self.definition,
            "clue_type": self.clue_type.value,
            "indicator": self.indicator,
            "fodder": self.fodder,
            "explanation": self.explanation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CrypticClue:
        return cls(
            clue_id=data["clue_id"],
            slot_id=data["slot_id"],
            number=data["number"],
            direction=Direction(data["direction"]),
            surface_text=data["surface_text"],
            length=data["length"],
            answer=data["answer"],
            definition=data["definition"],
            clue_type=ClueType(data["clue_type"]),
            indicator=data.get("indicator", ""),
            fodder=data.get("fodder", ""),
            explanation=data.get("explanation", ""),
        )


@dataclass
class CrosswordGrid:
    grid_id: str
    title: str
    size_rows: int
    size_cols: int
    cells: List[List[str]]  # '#' indicates black cell, letter or '' indicates fillable
    slots: List[WordSlot] = field(default_factory=list)
    clues: List[CrypticClue] = field(default_factory=list)
    symmetry: str = "ROTATIONAL_180"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_id": self.grid_id,
            "title": self.title,
            "size_rows": self.size_rows,
            "size_cols": self.size_cols,
            "cells": self.cells,
            "slots": [s.to_dict() for s in self.slots],
            "clues": [c.to_dict() for c in self.clues],
            "symmetry": self.symmetry,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CrosswordGrid:
        return cls(
            grid_id=data["grid_id"],
            title=data["title"],
            size_rows=data["size_rows"],
            size_cols=data["size_cols"],
            cells=data["cells"],
            slots=[WordSlot.from_dict(s) for s in data.get("slots", [])],
            clues=[CrypticClue.from_dict(c) for c in data.get("clues", [])],
            symmetry=data.get("symmetry", "ROTATIONAL_180"),
        )


@dataclass
class SessionDelta:
    delta_id: str
    session_id: str
    row: int
    col: int
    char: str
    prev_char: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SolverSession:
    session_id: str
    puzzle_id: str
    user_id: str
    cells_entered: Dict[str, str] = field(default_factory=dict)  # "r,c" -> char
    version: int = 1
    updated_at: float = field(default_factory=time.time)
    is_complete: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "puzzle_id": self.puzzle_id,
            "user_id": self.user_id,
            "cells_entered": self.cells_entered,
            "version": self.version,
            "updated_at": self.updated_at,
            "is_complete": self.is_complete,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SolverSession:
        return cls(
            session_id=data["session_id"],
            puzzle_id=data["puzzle_id"],
            user_id=data.get("user_id", "default_user"),
            cells_entered=data.get("cells_entered", {}),
            version=data.get("version", 1),
            updated_at=data.get("updated_at", time.time()),
            is_complete=data.get("is_complete", False),
        )


@dataclass
class SynthesisJob:
    job_id: str
    status: JobStatus
    grid_size: int
    backtracks_count: int = 0
    pruned_candidates_count: int = 0
    joules_dissipated: float = 0.0
    progress_pct: float = 0.0
    result_grid: Optional[CrosswordGrid] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "grid_size": self.grid_size,
            "backtracks_count": self.backtracks_count,
            "pruned_candidates_count": self.pruned_candidates_count,
            "joules_dissipated": self.joules_dissipated,
            "progress_pct": self.progress_pct,
            "result_grid_id": self.result_grid.grid_id if self.result_grid else None,
            "error": self.error,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


@dataclass
class LandauerSearchAudit:
    search_id: str
    total_backtracks: int
    candidate_domain_erased_bits: float
    joules_dissipated: float
    pruned_branches_ratio: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FeedbackItem:
    feedback_id: str
    category: str
    comment: str
    timestamp: float = field(default_factory=time.time)
    generation: str = "gen_01"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
