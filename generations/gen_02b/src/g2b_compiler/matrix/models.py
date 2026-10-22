"""Multi-Tier Axiom & Usability Models for System G2b."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class AxiomTier(str, Enum):
    TIER_1_STRUCTURAL = "tier_1_structural"
    TIER_2_USABILITY = "tier_2_usability"
    TIER_3_DOMAIN = "tier_3_domain"


@dataclass(frozen=True)
class Tier1StructuralRule:
    rule_id: str
    name: str
    formal_predicate: str
    description: str


@dataclass(frozen=True)
class Tier2UsabilityHeuristic:
    heuristic_id: str
    name: str
    category: str  # "nielsen_norman" | "psychophysical" | "calm_tech"
    description: str
    audit_rule: str
    is_hard_gate: bool = False  # Allows stateful human override if False


@dataclass(frozen=True)
class Tier3DomainBenchmark:
    benchmark_id: str
    domain_archetype: str
    name: str
    description: str
    non_negotiable: bool = True


@dataclass
class MultiTierAuditResult:
    passed: bool
    tier_1_passed: bool
    tier_2_passed: bool
    tier_3_passed: bool
    tier_1_violations: List[str] = field(default_factory=list)
    tier_2_violations: List[Dict[str, Any]] = field(default_factory=list)  # {heuristic_id, element_or_state, message, component_hash}
    tier_3_violations: List[str] = field(default_factory=list)
    applied_overrides: List[str] = field(default_factory=list)
    unresolved_heuristic_violations: List[Dict[str, Any]] = field(default_factory=list)
    audit_summary: str = ""


class MultiTierAxiomViolation(Exception):
    """Raised when compilation fails Tier 1 structural or un-overridden Tier 2/3 rules."""
    pass
