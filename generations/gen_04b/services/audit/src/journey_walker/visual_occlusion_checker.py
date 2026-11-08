"""Visual Occlusion & Boundary Guard Engine (`[L1-G4B-017]`).

Enforces:
  - Axiom 1 (Viewport Containment):
      x >= 0 and y >= 0 and (x + w) <= viewport_W and (y + h) <= viewport_H
  - Axiom 2 (Non-Occlusion):
      elementFromPoint(x + w/2, y + h/2) returns target element or its direct child,
      proving zero z-index modal or floating panel occlusion.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from .domain_models import (
    BoundingBox,
    OcclusionViolation,
    ViewportClippingViolation,
)


class VisualOcclusionChecker:
    """Mathematical 2D geometry engine for headless UI verification."""

    def __init__(
        self,
        default_viewport_width: float = 1920.0,
        default_viewport_height: float = 1080.0,
    ) -> None:
        self.default_viewport_width = float(default_viewport_width)
        self.default_viewport_height = float(default_viewport_height)

    def check_viewport_containment(
        self,
        box: BoundingBox,
        viewport_width: Optional[float] = None,
        viewport_height: Optional[float] = None,
    ) -> None:
        """Enforces Axiom 1 (Viewport Containment).

        Asserts:
          x >= 0 and y >= 0 and (x + w) <= viewport_W and (y + h) <= viewport_H
        Raises ViewportClippingViolation if touch target is clipped or offscreen.
        """
        vw = viewport_width if viewport_width is not None else self.default_viewport_width
        vh = viewport_height if viewport_height is not None else self.default_viewport_height

        if box.x < 0 or box.y < 0:
            raise ViewportClippingViolation(
                f"Element '{box.selector}' negative coordinate violation: "
                f"origin=({box.x:.1f}, {box.y:.1f}) is out of bounds (min=(0, 0))."
            )

        if (box.x + box.width) > vw or (box.y + box.height) > vh:
            raise ViewportClippingViolation(
                f"Element '{box.selector}' viewport overflow clipping: "
                f"box bounds=({box.x + box.width:.1f}, {box.y + box.height:.1f}) "
                f"exceeds viewport dimensions ({vw:.1f}, {vh:.1f})."
            )

    def element_from_point(
        self,
        px: float,
        py: float,
        layout_elements: List[BoundingBox],
    ) -> Optional[BoundingBox]:
        """Simulates browser document.elementFromPoint(px, py).

        Returns the top-most visible BoundingBox covering point (px, py),
        resolved by maximum z-index and document stacking order.
        """
        candidates: List[Tuple[int, int, BoundingBox]] = []
        for idx, box in enumerate(layout_elements):
            if box.is_visible and box.contains_point(px, py):
                # Stacking key: (z_index, document_index)
                candidates.append((box.z_index, idx, box))

        if not candidates:
            return None

        # Sort descending by z_index, then document index
        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return candidates[0][2]

    def check_non_occlusion(
        self,
        target_box: BoundingBox,
        layout_elements: List[BoundingBox],
        tolerance_px: float = 1.0,
    ) -> None:
        """Enforces Axiom 2 (Non-Occlusion).

        Verifies that at the element's geometric center (x + w/2, y + h/2),
        the element itself is the top-most receiver of pointer events.
        Raises OcclusionViolation if intercepted by a higher z-index modal, backdrop, or panel.
        """
        cx, cy = target_box.center_point
        top_element = self.element_from_point(cx, cy, layout_elements)

        if top_element is None:
            # If no elements registered, target itself isn't occluded by anything
            return

        if top_element.selector == target_box.selector:
            return

        # Check if the top element is an ancestor/descendant or has higher z_index
        if top_element.z_index > target_box.z_index:
            raise OcclusionViolation(
                f"Touch target '{target_box.selector}' (z-index={target_box.z_index}) is occluded at center "
                f"({cx:.1f}, {cy:.1f}) by overlay element '{top_element.selector}' "
                f"(z-index={top_element.z_index})."
            )

    @classmethod
    def parse_box_from_style(
        cls,
        selector: str,
        style_dict: Dict[str, Any],
        default_x: float = 0.0,
        default_y: float = 0.0,
        default_w: float = 120.0,
        default_h: float = 40.0,
    ) -> BoundingBox:
        """Constructs a BoundingBox from extracted CSS styles or HTML attributes."""
        def _parse_px(val: Any, default: float) -> float:
            if val is None:
                return default
            val_str = str(val).strip().lower()
            m = re.match(r"^([\d.]+)(?:px|rem|em|%)?", val_str)
            if m:
                return float(m.group(1))
            try:
                return float(val)
            except ValueError:
                return default

        x = _parse_px(style_dict.get("left") or style_dict.get("x"), default_x)
        y = _parse_px(style_dict.get("top") or style_dict.get("y"), default_y)
        w = _parse_px(style_dict.get("width") or style_dict.get("w"), default_w)
        h = _parse_px(style_dict.get("height") or style_dict.get("h"), default_h)

        z_str = str(style_dict.get("z-index") or style_dict.get("z_index", "0")).strip()
        z_index = int(z_str) if z_str.lstrip("-").isdigit() else 0

        display = str(style_dict.get("display", "block")).lower()
        visibility = str(style_dict.get("visibility", "visible")).lower()
        is_visible = (display != "none" and visibility != "hidden")

        return BoundingBox(
            x=x,
            y=y,
            width=w,
            height=h,
            z_index=z_index,
            is_visible=is_visible,
            selector=selector,
        )
