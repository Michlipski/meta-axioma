"""Studio CSS Template & Design Tokens (`studio_css_template.py`).

Enforces:
- Canonical CSS variables and design tokens (--bg-base: #0a0d14, --bg-surface: #121622, --accent-cyan: #00e5ff, etc.).
- Fluid CSS Grid layout (.studio-container: 1fr 340px, 1fr auto, 100vh, 100vw).
- Guaranteed zero horizontal scrollbars and zero clipped viewports.
- Touch action containment (`touch-action: none`) for mobile/pointer stability.
- Zero-CDN compliance ([HERM-005]): 100% self-contained CSS without external fonts or imports.
"""

from __future__ import annotations

from generations.gen_04b.services.research.src.contract_ui import LayoutArchetype


class StudioCSSTemplate:
    """Renders canonical responsive CSS stylesheets for Tactile Studio applications."""

    @staticmethod
    def render_css(archetype: LayoutArchetype = LayoutArchetype.STUDIO_SPLIT_PANE) -> str:
        """Emits the full standalone CSS for the specified layout archetype."""
        base_css = '''/* =========================================================================
 * Meta-Axioma Tactile Studio Architecture CSS [HERM-005 Zero-CDN]
 * High-Contrast Dark Theme, Fluid CSS Grid, Responsive Viewports
 * ========================================================================= */

:root {
  /* Color Palette Tokens */
  --bg-base: #0a0d14;
  --bg-surface: #121622;
  --bg-surface-elevated: #1a2030;
  --bg-surface-hover: #222b40;
  --border-subtle: #242c40;
  --border-focus: #3b82f6;

  /* Typography Colors */
  --text-primary: #f0f4fc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;

  /* Semantic Accent Accents */
  --accent-cyan: #00e5ff;
  --accent-emerald: #10b981;
  --accent-rose: #f43f5e;
  --accent-amber: #f59e0b;
  --accent-indigo: #6366f1;

  /* Typography Stack - System Native, Zero CDN */
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;

  /* Elevation Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -1px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.6), 0 4px 6px -2px rgba(0, 0, 0, 0.4);
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: var(--bg-base);
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 14px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* --- Studio Container Grid Archetype --- */
.studio-container {
  display: grid;
  grid-template-columns: 1fr 340px;
  grid-template-rows: 1fr auto;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* --- Top Header / App Banner --- */
.studio-header {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle);
  height: 48px;
  z-index: 10;
}

.studio-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 10px;
}

.studio-badge {
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background-color: rgba(0, 229, 255, 0.12);
  color: var(--accent-cyan);
  border: 1px solid rgba(0, 229, 255, 0.3);
}

.studio-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn {
  background-color: var(--bg-surface-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn:hover {
  background-color: var(--bg-surface-hover);
  border-color: var(--accent-cyan);
}

.btn-primary {
  background-color: rgba(0, 229, 255, 0.15);
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
}

.btn-primary:hover {
  background-color: rgba(0, 229, 255, 0.25);
}

/* --- Spatial Interactive Canvas --- */
.canvas-pane {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: var(--bg-base);
  background-image: 
    radial-gradient(circle at 1px 1px, rgba(255, 255, 255, 0.05) 1px, transparent 0);
  background-size: 24px 24px;
}

#tactile-canvas {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  touch-action: none; /* Prevents mobile gesture interference */
  user-select: none;
  cursor: grab;
}

#tactile-canvas:active {
  cursor: grabbing;
}

#canvas-world {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  transform-origin: 0 0;
  pointer-events: none;
}

/* Tactile Draggable Nodes */
.tactile-node {
  position: absolute;
  pointer-events: auto;
  min-width: 140px;
  padding: 12px 16px;
  background-color: var(--bg-surface-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  box-shadow: var(--shadow-md);
  cursor: move;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.tactile-node:hover {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.2);
}

.tactile-node.selected {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 16px rgba(0, 229, 255, 0.35);
  outline: 2px solid var(--accent-cyan);
}

.node-title {
  font-weight: 600;
  font-size: 13px;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.node-meta {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-secondary);
}

/* --- Inspector HUD Pane --- */
.inspector-pane {
  background-color: var(--bg-surface);
  border-left: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
  z-index: 5;
}

.inspector-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-subtle);
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.inspector-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
}

.inspector-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.inspector-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.inspector-value {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-primary);
  background-color: var(--bg-base);
  padding: 8px 10px;
  border-radius: 4px;
  border: 1px solid var(--border-subtle);
  word-break: break-all;
}

/* --- Bottom Timeline & Narrative Scrubber HUD --- */
.studio-footer {
  grid-column: 1 / -1;
  background-color: var(--bg-surface);
  border-top: 1px solid var(--border-subtle);
  padding: 12px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 10;
}

.narrative-hud-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: rgba(0, 229, 255, 0.05);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 6px;
  padding: 8px 14px;
}

.narrative-tag {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--accent-cyan);
  background-color: rgba(0, 229, 255, 0.15);
  padding: 2px 6px;
  border-radius: 3px;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.narrative-text {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
  flex: 1;
}

.narrative-timestamp {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
}

.timeline-scrubber {
  display: flex;
  align-items: center;
  gap: 14px;
}

.timeline-slider {
  flex: 1;
  accent-color: var(--accent-cyan);
}

.timeline-ticks {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-secondary);
}

/* Responsive Breakpoints */
@media (max-width: 900px) {
  .studio-container {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr 240px auto;
  }
  .inspector-pane {
    border-left: none;
    border-top: 1px solid var(--border-subtle);
  }
}
'''
        if archetype == LayoutArchetype.REACTIVE_GRID:
            # Overrides for reactive matrix
            grid_override = '''
/* Reactive Grid Archetype Specifics */
.studio-container.reactive-grid-layout {
  grid-template-columns: 1fr;
  grid-template-rows: 1fr auto;
}
.grid-matrix {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 24px;
  overflow-y: auto;
}
'''
            return base_css + grid_override
        elif archetype == LayoutArchetype.TIMELINE_CONSOLE:
            # Overrides for timeline console
            console_override = '''
/* Timeline Console Archetype Specifics */
.studio-container.timeline-console-layout {
  grid-template-columns: 1fr 380px;
  grid-template-rows: 1fr 180px;
}
.audit-stream-pane {
  font-family: var(--font-mono);
  font-size: 12px;
  overflow-y: auto;
  background-color: var(--bg-base);
  padding: 12px;
  border-top: 1px solid var(--border-subtle);
}
'''
            return base_css + console_override

        return base_css
