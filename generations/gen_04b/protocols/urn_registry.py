"""Generation 4b Universal Symbol URN Taxonomy & Registry (`protocols/urn_registry.py`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- Consistent URN scheme: urn:axioma:g4b:<service_or_domain>:<entity_name>#<version_or_symbol>
- Deterministic symbol resolution across Sovereign Services (Research, Builder, Audit, Telemetry, Governance).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional, Set


class URNFormatError(ValueError):
    """Raised when a symbol URN does not conform to the G4b canonical scheme."""
    pass


URN_REGEX = re.compile(
    r"^urn:axioma:g4b:(?P<domain>[a-zA-Z0-9_\-]+):(?P<entity>[a-zA-Z0-9_\-]+)(?:#(?P<symbol>[a-zA-Z0-9_\.\-]+))?$"
)


@dataclass(frozen=True)
class SymbolURN:
    """Canonical representation of a Generation 4b Universal Symbol URN."""
    domain: str
    entity: str
    symbol: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.domain:
            raise URNFormatError("URN domain must not be empty.")
        if not self.entity:
            raise URNFormatError("URN entity must not be empty.")

    @classmethod
    def parse(cls, urn_string: str) -> SymbolURN:
        match = URN_REGEX.match(urn_string)
        if not match:
            raise URNFormatError(
                f"Invalid G4b URN format: '{urn_string}'. "
                "Expected pattern: urn:axioma:g4b:<domain>:<entity>[#<symbol>]"
            )
        groups = match.groupdict()
        return cls(
            domain=groups["domain"],
            entity=groups["entity"],
            symbol=groups.get("symbol"),
        )

    def to_string(self) -> str:
        base = f"urn:axioma:g4b:{self.domain}:{self.entity}"
        if self.symbol:
            return f"{base}#{self.symbol}"
        return base

    def __str__(self) -> str:
        return self.to_string()


@dataclass
class URNRegistry:
    """In-memory registry and symbol locator for Generation 4b service mesh."""
    _entries: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def register_symbol(
        self,
        urn: str | SymbolURN,
        provider_service: str,
        schema_version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SymbolURN:
        parsed = urn if isinstance(urn, SymbolURN) else SymbolURN.parse(urn)
        canonical_str = parsed.to_string()
        self._entries[canonical_str] = {
            "urn": canonical_str,
            "domain": parsed.domain,
            "entity": parsed.entity,
            "symbol": parsed.symbol,
            "provider_service": provider_service,
            "schema_version": schema_version,
            "metadata": metadata or {},
        }
        return parsed

    def resolve(self, urn: str | SymbolURN) -> Optional[Dict[str, Any]]:
        parsed = urn if isinstance(urn, SymbolURN) else SymbolURN.parse(urn)
        return self._entries.get(parsed.to_string())

    def list_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        return [entry for entry in self._entries.values() if entry["domain"] == domain]

    def list_by_service(self, service: str) -> List[Dict[str, Any]]:
        return [entry for entry in self._entries.values() if entry["provider_service"] == service]

    def clear(self) -> None:
        self._entries.clear()


# Default global registry instance
GLOBAL_URN_REGISTRY = URNRegistry()
