"""ContractIR-UI Declarative Specification Schema (`services/research/src/contract_ui.py`).

Enforces:
- [L1-G3B-011] Universal Compositional Contract IR & Domain Invariants.
- [L1-G4B-001] Decoupled Research Service Invariants.
- [L1-G4B-002] Zero-Code Research Boundary (purely declarative data structures).
- Waterloo SYDE 361 Human Ergonomics (P_1): Hotkeys, responsive viewports, and plain-English narrative translation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class LayoutArchetype(str, Enum):
    """Canonical, responsive zero-CDN layout archetypes for synthesized frontends."""
    STUDIO_SPLIT_PANE = "STUDIO_SPLIT_PANE"   # Interactive Canvas (70%) + Inspector HUD (30%) + Bottom Scrubber
    REACTIVE_GRID     = "REACTIVE_GRID"       # Filterable card/node matrix with inspector modal
    TIMELINE_CONSOLE  = "TIMELINE_CONSOLE"    # Central scrubber HUD with audit stream & graph


@dataclass(frozen=True)
class ErgonomicsContract:
    """Human ergonomics constraints and interaction policies."""
    enable_undo_hotkeys: bool = True          # Cmd+Z / Cmd+Shift+Z / Cmd+Y
    enable_escape_deselect: bool = True       # Esc resets focus/selection
    enable_space_playback: bool = True        # Space toggles simulation/playback
    viewport_min_width: int = 900             # Minimum responsive width
    viewport_min_height: int = 550            # Minimum responsive height

    def validate(self) -> None:
        """Validates ergonomics constraints."""
        if self.viewport_min_width <= 0:
            raise ValueError(f"viewport_min_width must be positive, got {self.viewport_min_width}")
        if self.viewport_min_height <= 0:
            raise ValueError(f"viewport_min_height must be positive, got {self.viewport_min_height}")


@dataclass(frozen=True)
class UIContractSpecification:
    """The sovereign declarative UI specification emitted by the Research Service.
    
    Provides a formal UI contract consumed by services/builder/ui_scaffolder/
    without writing concrete application code in the research service.
    """
    archetype: LayoutArchetype
    ergonomics: ErgonomicsContract
    workspace_title: str
    narrative_context: str
    inspector_fields: List[str] = field(default_factory=list)
    timeline_event_types: List[str] = field(default_factory=list)

    def validate(self) -> None:
        """Validates contract invariants."""
        if not self.workspace_title.strip():
            raise ValueError("workspace_title must not be empty.")
        if not self.narrative_context.strip():
            raise ValueError("narrative_context must not be empty.")
        self.ergonomics.validate()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes contract specification to a plain dictionary."""
        return {
            "archetype": self.archetype.value,
            "ergonomics": asdict(self.ergonomics),
            "workspace_title": self.workspace_title,
            "narrative_context": self.narrative_context,
            "inspector_fields": list(self.inspector_fields),
            "timeline_event_types": list(self.timeline_event_types),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UIContractSpecification:
        """Deserializes contract specification from dictionary."""
        ergonomics_data = data.get("ergonomics", {})
        ergonomics = ErgonomicsContract(
            enable_undo_hotkeys=bool(ergonomics_data.get("enable_undo_hotkeys", True)),
            enable_escape_deselect=bool(ergonomics_data.get("enable_escape_deselect", True)),
            enable_space_playback=bool(ergonomics_data.get("enable_space_playback", True)),
            viewport_min_width=int(ergonomics_data.get("viewport_min_width", 900)),
            viewport_min_height=int(ergonomics_data.get("viewport_min_height", 550)),
        )
        return cls(
            archetype=LayoutArchetype(data["archetype"]),
            ergonomics=ergonomics,
            workspace_title=str(data["workspace_title"]),
            narrative_context=str(data.get("narrative_context", "")),
            inspector_fields=list(data.get("inspector_fields", [])),
            timeline_event_types=list(data.get("timeline_event_types", [])),
        )
