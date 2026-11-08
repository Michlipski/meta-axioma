"""Tactile Canvas Vanilla JS & Mathematical Coordinate Engine (`tactile_canvas_template.py`).

Enforces:
- Fluid pointer capture (`setPointerCapture(e.pointerId)`).
- Coordinate Normalization: X_spatial = (X_screen - offset_X) / scale.
- Boundary Clamping: Strictly bounds objects within [0, W_canvas - W_node] x [0, H_canvas - H_node].
- Fluid ResizeObserver: Responsive container tracking eliminating rigid 600x400 viewports.
- Zero-CDN compliance ([HERM-005]): 100% self-contained vanilla JavaScript.
"""

from __future__ import annotations

from typing import Tuple


def screen_to_spatial(
    screen_x: float,
    screen_y: float,
    offset_x: float,
    offset_y: float,
    scale: float,
) -> Tuple[float, float]:
    """Translates screen coordinates to internal spatial canvas coordinates.
    
    Formula:
        X_spatial = (X_screen - offset_X) / scale
        Y_spatial = (Y_screen - offset_Y) / scale
    """
    if scale <= 0:
        raise ValueError(f"Scale must be strictly positive, got {scale}")
    spatial_x = (screen_x - offset_x) / scale
    spatial_y = (screen_y - offset_y) / scale
    return spatial_x, spatial_y


def clamp_coordinates(
    spatial_x: float,
    spatial_y: float,
    node_width: float,
    node_height: float,
    canvas_width: float,
    canvas_height: float,
) -> Tuple[float, float]:
    """Mathematically clamps node coordinates within the canvas bounding rectangle.
    
    Guarantees that an element dragged to (-500, -500) or (9999, 9999) clamps strictly
    within [0, max(0, canvas_width - node_width)] x [0, max(0, canvas_height - node_height)].
    """
    max_x = max(0.0, float(canvas_width) - float(node_width))
    max_y = max(0.0, float(canvas_height) - float(node_height))

    clamped_x = max(0.0, min(max_x, float(spatial_x)))
    clamped_y = max(0.0, min(max_y, float(spatial_y)))

    return clamped_x, clamped_y


class TactileCanvasTemplate:
    """Renders canonical vanilla JS spatial pointer tracker & boundary containment controller."""

    @staticmethod
    def render_js() -> str:
        """Emits the full TactileCanvasController vanilla JS implementation."""
        return '''// =========================================================================
// TactileCanvasController: Zero-CDN Fluid Pointer & Spatial Engine
// Enforces [HERM-005], Coordinate Normalization, Boundary Clamping, Pointer Capture
// =========================================================================

class TactileCanvasController {
  constructor(canvasElement, options = {}) {
    this.canvas = canvasElement;
    this.world = canvasElement.querySelector('#canvas-world') || canvasElement;
    this.options = Object.assign({
      minScale: 0.25,
      maxScale: 3.5,
      defaultScale: 1.0,
      enablePan: true,
      enableZoom: true,
      enableBoundaryClamping: true,
      onNodeSelect: null,
      onNodeMove: null,
      onStateChange: null
    }, options);

    // Spatial Transform Matrix State
    this.panOffset = { x: 0, y: 0 };
    this.scale = this.options.defaultScale;
    this.canvasWidth = this.canvas.clientWidth || 900;
    this.canvasHeight = this.canvas.clientHeight || 550;

    // Interaction State
    this.isPanning = false;
    this.draggedNode = null;
    this.dragStart = { x: 0, y: 0 };
    this.nodeStartPos = { x: 0, y: 0 };
    this.selectedNodeId = null;

    this._initResizeObserver();
    this._bindEvents();
    this._applyTransform();
  }

  // --- Coordinate Normalization ---
  // X_spatial = (X_screen - offset_X) / scale
  screenToSpatial(clientX, clientY) {
    const rect = this.canvas.getBoundingClientRect();
    const screenX = clientX - rect.left;
    const screenY = clientY - rect.top;
    return {
      x: (screenX - this.panOffset.x) / this.scale,
      y: (screenY - this.panOffset.y) / this.scale
    };
  }

  spatialToScreen(spatialX, spatialY) {
    const rect = this.canvas.getBoundingClientRect();
    return {
      x: rect.left + this.panOffset.x + (spatialX * this.scale),
      y: rect.top + this.panOffset.y + (spatialY * this.scale)
    };
  }

  // --- Boundary Clamping ---
  // Guarantees elements never escape outside canvas dimensions
  clampNodePosition(spatialX, spatialY, nodeWidth, nodeHeight) {
    const maxX = Math.max(0, this.canvasWidth - nodeWidth);
    const maxY = Math.max(0, this.canvasHeight - nodeHeight);
    return {
      x: Math.max(0, Math.min(maxX, spatialX)),
      y: Math.max(0, Math.min(maxY, spatialY))
    };
  }

  // --- Fluid ResizeObserver ---
  _initResizeObserver() {
    if (typeof ResizeObserver !== 'undefined') {
      this.resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          const { width, height } = entry.contentRect;
          if (width > 0 && height > 0) {
            this.canvasWidth = width;
            this.canvasHeight = height;
            this._clampAllNodes();
          }
        }
      });
      this.resizeObserver.observe(this.canvas);
    }
  }

  _clampAllNodes() {
    if (!this.options.enableBoundaryClamping) return;
    const nodes = this.world.querySelectorAll('.tactile-node');
    nodes.forEach(node => {
      const curX = parseFloat(node.dataset.x || 0);
      const curY = parseFloat(node.dataset.y || 0);
      const w = node.offsetWidth || 120;
      const h = node.offsetHeight || 60;
      const clamped = this.clampNodePosition(curX, curY, w, h);
      node.dataset.x = clamped.x;
      node.dataset.y = clamped.y;
      node.style.transform = `translate(${clamped.x}px, ${clamped.y}px)`;
    });
  }

  _applyTransform() {
    this.world.style.transform = `translate(${this.panOffset.x}px, ${this.panOffset.y}px) scale(${this.scale})`;
    this.world.style.transformOrigin = '0 0';
  }

  // --- Pointer & Spatial Events ---
  _bindEvents() {
    const canvas = this.canvas;

    // Pointer Down: Start Drag or Pan with Pointer Capture
    canvas.addEventListener('pointerdown', (e) => {
      const targetNode = e.target.closest('.tactile-node');

      if (targetNode) {
        // Node dragging initiated
        this.draggedNode = targetNode;
        targetNode.setPointerCapture(e.pointerId);
        
        const spatial = this.screenToSpatial(e.clientX, e.clientY);
        this.dragStart = spatial;
        this.nodeStartPos = {
          x: parseFloat(targetNode.dataset.x || 0),
          y: parseFloat(targetNode.dataset.y || 0)
        };

        this.selectNode(targetNode.dataset.id || targetNode.id);
        e.stopPropagation();
      } else if (this.options.enablePan && (e.button === 0 || e.button === 1)) {
        // Background panning initiated
        this.isPanning = true;
        canvas.setPointerCapture(e.pointerId);
        this.panStart = {
          clientX: e.clientX,
          clientY: e.clientY,
          initialOffsetX: this.panOffset.x,
          initialOffsetY: this.panOffset.y
        };
      }
    });

    // Pointer Move: Active Dragging with Normalization and Boundary Clamping
    canvas.addEventListener('pointermove', (e) => {
      if (this.draggedNode) {
        const currentSpatial = this.screenToSpatial(e.clientX, e.clientY);
        const dx = currentSpatial.x - this.dragStart.x;
        const dy = currentSpatial.y - this.dragStart.y;

        const targetX = this.nodeStartPos.x + dx;
        const targetY = this.nodeStartPos.y + dy;
        const nodeW = this.draggedNode.offsetWidth || 120;
        const nodeH = this.draggedNode.offsetHeight || 60;

        let finalPos = { x: targetX, y: targetY };
        if (this.options.enableBoundaryClamping) {
          finalPos = this.clampNodePosition(targetX, targetY, nodeW, nodeH);
        }

        this.draggedNode.dataset.x = finalPos.x;
        this.draggedNode.dataset.y = finalPos.y;
        this.draggedNode.style.transform = `translate(${finalPos.x}px, ${finalPos.y}px)`;

        if (this.options.onNodeMove) {
          this.options.onNodeMove(this.draggedNode.dataset.id, finalPos.x, finalPos.y);
        }
      } else if (this.isPanning && this.panStart) {
        const dx = e.clientX - this.panStart.clientX;
        const dy = e.clientY - this.panStart.clientY;
        this.panOffset.x = this.panStart.initialOffsetX + dx;
        this.panOffset.y = this.panStart.initialOffsetY + dy;
        this._applyTransform();
      }
    });

    // Pointer Up & Cancel: Release Pointer Capture
    const endInteraction = (e) => {
      if (this.draggedNode) {
        try {
          this.draggedNode.releasePointerCapture(e.pointerId);
        } catch (_) {}
        this.draggedNode = null;
      }
      if (this.isPanning) {
        try {
          canvas.releasePointerCapture(e.pointerId);
        } catch (_) {}
        this.isPanning = false;
        this.panStart = null;
      }
    };

    canvas.addEventListener('pointerup', endInteraction);
    canvas.addEventListener('pointercancel', endInteraction);

    // Zoom on Wheel with Cursor Anchor
    if (this.options.enableZoom) {
      canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        const rect = canvas.getBoundingClientRect();
        const cursorScreenX = e.clientX - rect.left;
        const cursorScreenY = e.clientY - rect.top;

        const spatialBefore = {
          x: (cursorScreenX - this.panOffset.x) / this.scale,
          y: (cursorScreenY - this.panOffset.y) / this.scale
        };

        const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
        const newScale = Math.max(this.options.minScale, Math.min(this.options.maxScale, this.scale * zoomFactor));

        if (newScale !== this.scale) {
          this.scale = newScale;
          this.panOffset.x = cursorScreenX - spatialBefore.x * this.scale;
          this.panOffset.y = cursorScreenY - spatialBefore.y * this.scale;
          this._applyTransform();
        }
      }, { passive: false });
    }
  }

  selectNode(nodeId) {
    this.selectedNodeId = nodeId;
    const allNodes = this.world.querySelectorAll('.tactile-node');
    allNodes.forEach(node => {
      if ((node.dataset.id || node.id) === nodeId) {
        node.classList.add('selected');
      } else {
        node.classList.remove('selected');
      }
    });

    if (this.options.onNodeSelect) {
      this.options.onNodeSelect(nodeId);
    }
  }

  deselectAll() {
    this.selectedNodeId = null;
    const allNodes = this.world.querySelectorAll('.tactile-node');
    allNodes.forEach(node => node.classList.remove('selected'));
    if (this.options.onNodeSelect) {
      this.options.onNodeSelect(null);
    }
  }

  resetViewport() {
    this.panOffset = { x: 0, y: 0 };
    this.scale = this.options.defaultScale;
    this._applyTransform();
  }
}
'''
