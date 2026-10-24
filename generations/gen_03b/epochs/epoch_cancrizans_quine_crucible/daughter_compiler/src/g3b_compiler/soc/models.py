"""Waterloo Systems Design Continuum: Situation of Concern (SoC) Models.

In the Waterloo Systems Design Engineering tradition, system design begins in the
messy, unstructured real-world context before any boundaries or solutions are set.

Enforces:
- [L1-G3B-000] The Situation of Concern Normalization Invariant: Regardless of entry tier,
  compilation cannot proceed to concept synthesis until a formal Situation of Concern (Tier 1)
  has been explicitly reconstructed, characterized, and certified.
- Fractal Decomposition: Macro (System) -> Meso (Subsystem) -> Micro (Interaction).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class SoCAltitude(str, Enum):
    """The altitude level of the Situation of Concern in system decomposition."""
    MACRO = "MACRO"      # System altitude: overall human struggle, organizational breakdown
    MESO = "MESO"        # Subsystem altitude: boundary tensions, offline sync, data flow frictions
    MICRO = "MICRO"      # Interaction altitude: cognitive load, accidental clicks, ergonomic barriers


class FrictionSeverity(str, Enum):
    """Severity of friction or breakdown in the situation."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ConstraintType(str, Enum):
    """Classification of boundary constraint in the environment."""
    TECHNICAL = "TECHNICAL"
    REGULATORY = "REGULATORY"
    ERGONOMIC = "ERGONOMIC"
    THERMODYNAMIC = "THERMODYNAMIC"
    RESOURCE = "RESOURCE"


@dataclass
class Actor:
    """An actor operating within the Situation of Concern."""
    name: str
    role: str
    motivations: List[str] = field(default_factory=list)
    frustrations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "motivations": self.motivations,
            "frustrations": self.frustrations,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Actor":
        return cls(
            name=data["name"],
            role=data.get("role", ""),
            motivations=data.get("motivations", []),
            frustrations=data.get("frustrations", []),
        )


@dataclass
class Friction:
    """A specific friction point, breakdown, or source of suffering in the SoC."""
    description: str
    severity: FrictionSeverity = FrictionSeverity.MEDIUM
    impact: str = ""
    trigger_conditions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "severity": self.severity.value,
            "impact": self.impact,
            "trigger_conditions": self.trigger_conditions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Friction":
        return cls(
            description=data["description"],
            severity=FrictionSeverity(data.get("severity", "MEDIUM")),
            impact=data.get("impact", ""),
            trigger_conditions=data.get("trigger_conditions", []),
        )


@dataclass
class EnvironmentalConstraint:
    """An unchangeable reality or hard boundary in the problem environment."""
    nature: ConstraintType
    description: str
    boundary_limit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nature": self.nature.value,
            "description": self.description,
            "boundary_limit": self.boundary_limit,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnvironmentalConstraint":
        return cls(
            nature=ConstraintType(data.get("nature", "TECHNICAL")),
            description=data["description"],
            boundary_limit=data.get("boundary_limit", ""),
        )


@dataclass
class SituationOfConcern:
    """Formalized Tier 1 Situation of Concern (SoC).

    Represents the problem space without any solution bias. All compilation
    must derive from this normalized representation.
    """
    soc_id: str
    title: str
    narrative: str
    altitude: SoCAltitude = SoCAltitude.MACRO
    actors: List[Actor] = field(default_factory=list)
    frictions: List[Friction] = field(default_factory=list)
    constraints: List[EnvironmentalConstraint] = field(default_factory=list)
    unmet_needs: List[str] = field(default_factory=list)
    induced_frictions: List[str] = field(default_factory=list)
    parent_soc_id: Optional[str] = None
    sub_socs: List["SituationOfConcern"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "soc_id": self.soc_id,
            "title": self.title,
            "narrative": self.narrative,
            "altitude": self.altitude.value,
            "actors": [a.to_dict() for a in self.actors],
            "frictions": [f.to_dict() for f in self.frictions],
            "constraints": [c.to_dict() for c in self.constraints],
            "unmet_needs": self.unmet_needs,
            "induced_frictions": self.induced_frictions,
            "parent_soc_id": self.parent_soc_id,
            "sub_socs": [s.to_dict() for s in self.sub_socs],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SituationOfConcern":
        return cls(
            soc_id=data["soc_id"],
            title=data["title"],
            narrative=data["narrative"],
            altitude=SoCAltitude(data.get("altitude", "MACRO")),
            actors=[Actor.from_dict(a) for a in data.get("actors", [])],
            frictions=[Friction.from_dict(f) for f in data.get("frictions", [])],
            constraints=[EnvironmentalConstraint.from_dict(c) for c in data.get("constraints", [])],
            unmet_needs=data.get("unmet_needs", []),
            induced_frictions=data.get("induced_frictions", []),
            parent_soc_id=data.get("parent_soc_id"),
            sub_socs=[cls.from_dict(s) for s in data.get("sub_socs", [])],
        )


@dataclass
class PitchInput:
    """Tier 2: Candidate Concept / Elevator Pitch input."""
    title: str
    elevator_pitch: str
    target_audience: str
    intended_features: List[str] = field(default_factory=list)
    solution_biases: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "elevator_pitch": self.elevator_pitch,
            "target_audience": self.target_audience,
            "intended_features": self.intended_features,
            "solution_biases": self.solution_biases,
        }


@dataclass
class ReferenceProductInput:
    """Tier 3: Existing 3rd-Party Reference Product / Benchmark input."""
    product_name: str
    historical_problem_solved: str
    known_limitations_and_bloat: List[str] = field(default_factory=list)
    reference_url_or_docs: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_name": self.product_name,
            "historical_problem_solved": self.historical_problem_solved,
            "known_limitations_and_bloat": self.known_limitations_and_bloat,
            "reference_url_or_docs": self.reference_url_or_docs,
        }
