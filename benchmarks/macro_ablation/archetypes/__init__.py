"""Benchmark Archetypes Registry for Meta-Axioma Macro-Bench."""

from typing import Dict, List
from ..domain_models import BenchmarkArchetype
from . import axioma_kv, axioma_flow, axioma_collab, axioma_gateway

ALL_ARCHETYPE_MODULES = {
    "axioma_kv": axioma_kv,
    "axioma_flow": axioma_flow,
    "axioma_collab": axioma_collab,
    "axioma_gateway": axioma_gateway,
}


def get_archetype_by_id(arch_id: str) -> BenchmarkArchetype:
    """Retrieves an archetype by ID or raises KeyError."""
    if arch_id not in ALL_ARCHETYPE_MODULES:
        raise KeyError(f"Archetype '{arch_id}' not found in registry. Available: {list(ALL_ARCHETYPE_MODULES.keys())}")
    return ALL_ARCHETYPE_MODULES[arch_id].get_archetype()


def get_all_archetypes() -> List[BenchmarkArchetype]:
    """Returns all 4 canonical benchmark archetypes."""
    return [mod.get_archetype() for mod in ALL_ARCHETYPE_MODULES.values()]


__all__ = [
    "ALL_ARCHETYPE_MODULES",
    "get_archetype_by_id",
    "get_all_archetypes",
    "axioma_kv",
    "axioma_flow",
    "axioma_collab",
    "axioma_gateway",
]
