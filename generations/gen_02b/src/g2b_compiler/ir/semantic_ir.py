"""Semantic Domain Intermediate Representation (Semantic IR) for System G1b.

Decouples high-level product intent from implementation details. Captures domain
entities (Nouns), lifecycle capabilities, and domain invariants without premature code emission.
Grounded in [L1-004] (Universal Grammar) and Anti-Greedy Decoupling.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    LIST_STRING = "list_string"
    JSON = "json"


@dataclass
class EntityField:
    name: str
    field_type: FieldType
    required: bool = True
    default: Any = None
    description: str = ""


@dataclass
class EntitySpec:
    name: str
    plural_name: str
    description: str
    fields: List[EntityField] = field(default_factory=list)
    primary_key: str = "id"


@dataclass
class DomainCapability:
    name: str
    description: str
    affected_entities: List[str] = field(default_factory=list)
    is_core_value: bool = False  # Marks primary Job-To-Be-Done state for Pareto budget


@dataclass
class DomainInvariant:
    invariant_id: str
    statement: str
    formal_rule: str
    is_hard_gate: bool = True


@dataclass
class SemanticDomainIR:
    app_id: str
    title: str
    tagline: str
    persona: str
    jtbd_summary: str
    entities: List[EntitySpec] = field(default_factory=list)
    capabilities: List[DomainCapability] = field(default_factory=list)
    invariants: List[DomainInvariant] = field(default_factory=list)
    initial_clean_seeds: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_entity(self, name: str) -> Optional[EntitySpec]:
        for e in self.entities:
            if e.name == name:
                return e
        return None

    @property
    def app_name(self) -> str:
        return self.title
