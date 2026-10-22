"""Domain Baseline Research Models for System G1b.

Defines domain archetypes, formal domain axioms, heuristics, table-stakes requirements,
and baseline audit reports for Phase 0 of the compilation pipeline.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class DomainArchetype(str, Enum):
    MEMORIZATION_SRS = "memorization_srs"
    CONSTRAINT_SOLVER_PUZZLE = "constraint_solver_puzzle"
    PRODUCTIVITY_KANBAN = "productivity_kanban"
    GENERAL_UTILITY = "general_utility"


class DomainBaselineViolation(Exception):
    """Raised when candidate specification or statechart violates domain non-negotiable table-stakes."""
    pass


@dataclass
class DomainAxiom:
    axiom_id: str
    name: str
    formal_rule: str
    description: str
    is_blocking: bool = True


@dataclass
class DomainHeuristic:
    title: str
    category: str  # "what_works" vs "what_fails"
    description: str
    impact_level: str = "critical"  # "critical", "high", "moderate"


@dataclass
class DomainBaselineReport:
    app_id: str
    archetype: DomainArchetype
    passed: bool
    table_stakes_audited: List[str]
    missing_table_stakes: List[str] = field(default_factory=list)
    anti_patterns_detected: List[str] = field(default_factory=list)
    applicable_axioms: List[DomainAxiom] = field(default_factory=list)
    heuristics: List[DomainHeuristic] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
