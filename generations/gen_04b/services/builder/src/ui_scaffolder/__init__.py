"""Tactile Studio UI Scaffolding Package (`services/builder/src/ui_scaffolder`).

Enforces:
- [HERM-005] Zero-CDN Invariant.
- [L1-G3B-011] Compositional Contract IR to Tactile UI Bijectivity.
- Waterloo SYDE 361 Human Ergonomics (P_1).
"""

from .narrative_hud_template import NarrativeHUDTemplate, format_narrative_diff
from .scaffolder import HermeticityViolation, UIScaffolder
from .studio_css_template import StudioCSSTemplate
from .tactile_canvas_template import (
    TactileCanvasTemplate,
    clamp_coordinates,
    screen_to_spatial,
)

__all__ = [
    "UIScaffolder",
    "HermeticityViolation",
    "TactileCanvasTemplate",
    "NarrativeHUDTemplate",
    "StudioCSSTemplate",
    "clamp_coordinates",
    "screen_to_spatial",
    "format_narrative_diff",
]
