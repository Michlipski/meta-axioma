"""Tactile Studio UI Scaffolding Engine (`ui_scaffolder/scaffolder.py`).

Enforces:
- [HERM-005]: Zero-CDN Invariant. Statically asserts zero external CDN or remote network links.
- [L1-G3B-011]: Compositional Contract IR to Tactile UI Bijectivity.
- [NEG-G1B-001]: Anti-Phantom Emission Gate (emits verified physical files to disk).
- Waterloo SYDE 361 Human Ergonomics (P_1): Hotkeys, pointer physics, and plain-English narrative translation.
"""

from __future__ import annotations

import html
import json
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional

from generations.gen_04b.services.research.src.contract_ui import (
    ErgonomicsContract,
    LayoutArchetype,
    UIContractSpecification,
)
from .narrative_hud_template import NarrativeHUDTemplate
from .studio_css_template import StudioCSSTemplate
from .tactile_canvas_template import TactileCanvasTemplate


class HermeticityViolation(Exception):
    """Raised when generated assets contain external HTTP/HTTPS CDN references violating [HERM-005]."""
    pass


class UIScaffolder:
    """Scaffolds complete, responsive, zero-CDN Tactile Studio web frontends."""

    def __init__(self, scaffolder_id: str = "scaffolder_g4b_tactile_studio") -> None:
        self.scaffolder_id = scaffolder_id

    @staticmethod
    def _verify_zero_cdn_compliance(files: Dict[str, str]) -> None:
        """Statically verifies that generated files contain zero external CDN or HTTP script/style imports."""
        external_url_pattern = re.compile(
            r"""(?:src|href)\s*=\s*['"]https?://[^'"]+['"]|@import\s+(?:url\(['"]?https?://|['"]https?://)""",
            re.IGNORECASE,
        )
        for filename, content in files.items():
            match = external_url_pattern.search(content)
            if match:
                raise HermeticityViolation(
                    f"External CDN link detected in '{filename}': {match.group(0)}. "
                    "Violates [HERM-005] Zero-CDN Hermeticity Invariant."
                )

    def generate_html(self, contract: UIContractSpecification) -> str:
        """Emits pure vanilla HTML5 structure adhering to the specified contract."""
        title = html.escape(contract.workspace_title)
        archetype_class = f"archetype-{contract.archetype.value.lower().replace('_', '-')}"
        
        # Build inspector field HTML placeholders
        inspector_fields_html = []
        for field_name in contract.inspector_fields:
            safe_field = html.escape(field_name)
            field_id = f"field-{re.sub(r'[^a-zA-Z0-9_-]', '_', field_name)}"
            inspector_fields_html.append(f"""          <div class="inspector-group">
            <span class="inspector-label">{safe_field}</span>
            <div class="inspector-value" id="{field_id}">—</div>
          </div>""")
        
        inspector_content = "\n".join(inspector_fields_html) if inspector_fields_html else """          <div class="inspector-group">
            <span class="inspector-label">Selection</span>
            <div class="inspector-value" id="field-selected-entity">No entity selected</div>
          </div>"""

        # Timeline event types tags
        event_tags_html = " ".join([
            f'<span class="studio-badge">{html.escape(ev)}</span>'
            for ev in contract.timeline_event_types
        ])

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>{title} — Tactile Studio</title>
  <!-- [HERM-005] Zero-CDN: Strictly local relative assets -->
  <link rel="stylesheet" href="style.css">
</head>
<body class="{archetype_class}">
  <div class="studio-container">
    <!-- Studio Header -->
    <header class="studio-header">
      <div class="studio-title">
        <span>{title}</span>
        <span class="studio-badge">{contract.archetype.value}</span>
        {event_tags_html}
      </div>
      <div class="studio-actions">
        <button class="btn" id="btn-undo" title="Undo (Cmd+Z)">Undo</button>
        <button class="btn" id="btn-redo" title="Redo (Cmd+Y)">Redo</button>
        <button class="btn btn-primary" id="btn-reset-view">Reset View</button>
      </div>
    </header>

    <!-- Interactive Spatial Canvas Pane -->
    <main class="canvas-pane">
      <div id="tactile-canvas">
        <div id="canvas-world">
          <!-- Dynamically managed tactile nodes -->
          <div class="tactile-node" id="node-seed-1" data-id="node-seed-1" data-x="80" data-y="80" style="transform: translate(80px, 80px);">
            <div class="node-title">Primary Domain Entity</div>
            <div class="node-meta">State: Active | Invariant: OK</div>
          </div>
          <div class="tactile-node" id="node-seed-2" data-id="node-seed-2" data-x="320" data-y="180" style="transform: translate(320px, 180px);">
            <div class="node-title">Secondary Reactive Entity</div>
            <div class="node-meta">State: Idle | Bounds: [0, W]</div>
          </div>
        </div>
      </div>
    </main>

    <!-- Inspector HUD Pane -->
    <aside class="inspector-pane">
      <div class="inspector-header">
        <span>Entity Inspector</span>
        <span class="studio-badge" id="inspector-selection-badge">None</span>
      </div>
      <div class="inspector-body" id="inspector-body">
{inspector_content}
      </div>
    </aside>

    <!-- Bottom Timeline & Narrative Scrubber HUD -->
    <footer class="studio-footer">
      <div class="narrative-hud-bar" id="narrative-hud">
        <span class="narrative-tag">HUD</span>
        <span class="narrative-text">Initializing ecosystem narrative...</span>
        <span class="narrative-timestamp">—</span>
      </div>
      <div class="timeline-scrubber">
        <button class="btn" id="btn-play-pause">▶ Play</button>
        <input type="range" class="timeline-slider" id="timeline-slider" min="0" max="100" value="0">
        <span class="timeline-ticks" id="timeline-tick-label">t = 0 / 100</span>
      </div>
    </footer>
  </div>

  <!-- [HERM-005] Zero-CDN: Strictly local application script -->
  <script src="app.js"></script>
</body>
</html>"""

    def generate_js(self, contract: UIContractSpecification) -> str:
        """Emits modular vanilla JS orchestrating canvas, narrative HUD, inspector, and ergonomics hotkeys."""
        canvas_js = TactileCanvasTemplate.render_js()
        narrative_js = NarrativeHUDTemplate.render_js()
        ergo = contract.ergonomics

        fields_json = json.dumps(contract.inspector_fields)
        initial_context = json.dumps(contract.narrative_context)

        return f"""// =========================================================================
// Tactile Studio Application Orchestrator
// Enforces [HERM-005] Zero-CDN, ErgonomicsContract Hotkeys, Inspector HUD Data Binding
// =========================================================================

{canvas_js}

{narrative_js}

// --- Inspector HUD Controller ---
class InspectorHUDController {{
  constructor(inspectorElement, fields = []) {{
    this.container = typeof inspectorElement === 'string' ? document.querySelector(inspectorElement) : inspectorElement;
    this.fields = fields;
    this.badge = document.querySelector('#inspector-selection-badge');
  }}

  bindEntity(entityData) {{
    if (!this.container) return;

    if (!entityData) {{
      if (this.badge) this.badge.textContent = 'None';
      this.fields.forEach(f => {{
        const el = document.getElementById('field-' + f.replace(/[^a-zA-Z0-9_-]/g, '_'));
        if (el) el.textContent = '—';
      }});
      const fallback = document.getElementById('field-selected-entity');
      if (fallback) fallback.textContent = 'No entity selected';
      return;
    }}

    const id = entityData.id || entityData.name || 'Selected';
    if (this.badge) this.badge.textContent = id;

    this.fields.forEach(f => {{
      const el = document.getElementById('field-' + f.replace(/[^a-zA-Z0-9_-]/g, '_'));
      if (el) {{
        el.textContent = entityData[f] !== undefined ? String(entityData[f]) : 'N/A';
      }}
    }});

    const fallback = document.getElementById('field-selected-entity');
    if (fallback) fallback.textContent = id;
  }}
}}

// --- Ergonomics & Application Bootstrap ---
document.addEventListener('DOMContentLoaded', () => {{
  const canvasEl = document.getElementById('tactile-canvas');
  const narrativeEl = document.getElementById('narrative-hud');
  const inspectorEl = document.getElementById('inspector-body');

  const inspectorFields = {fields_json};
  const narrativeContext = {initial_context};

  // 1. Initialize Controllers
  const narrativeController = new NarrativeHUDController(narrativeEl, {{
    contextTitle: '{html.escape(contract.workspace_title)}',
    defaultMessage: narrativeContext || 'Ready. Workspace initialized in baseline invariant equilibrium.'
  }});

  const inspectorController = new InspectorHUDController(inspectorEl, inspectorFields);

  // Undo/Redo State History Stack
  const historyStack = [];
  let historyIndex = -1;

  function pushState(actionName, snapshot) {{
    historyStack.splice(historyIndex + 1);
    historyStack.push({{ action: actionName, snapshot: snapshot }});
    historyIndex = historyStack.length - 1;
    narrativeController.ingestStateDiff({{ updated: {{ action: actionName }} }}, actionName);
  }}

  function executeUndo() {{
    if (historyIndex > 0) {{
      historyIndex--;
      const prev = historyStack[historyIndex];
      narrativeController.update(`Undo: Reverted to state "${{prev.action}}".`);
    }} else if (historyIndex === 0) {{
      historyIndex = -1;
      narrativeController.update('Undo: Reverted to initial baseline state.');
    }} else {{
      narrativeController.update('Undo: Already at oldest checkpoint.');
    }}
  }}

  function executeRedo() {{
    if (historyIndex < historyStack.length - 1) {{
      historyIndex++;
      const next = historyStack[historyIndex];
      narrativeController.update(`Redo: Restored state "${{next.action}}".`);
    }} else {{
      narrativeController.update('Redo: Already at newest checkpoint.');
    }}
  }}

  const canvasController = new TactileCanvasController(canvasEl, {{
    onNodeSelect: (nodeId) => {{
      if (nodeId) {{
        const node = document.getElementById(nodeId);
        const nodeData = {{
          id: nodeId,
          title: node ? node.querySelector('.node-title')?.textContent : nodeId,
          x: node ? parseFloat(node.dataset.x) : 0,
          y: node ? parseFloat(node.dataset.y) : 0,
          state: 'Active',
          status: 'Verified'
        }};
        inspectorController.bindEntity(nodeData);
        narrativeController.update(`Selected ${{nodeId}}. Coordinates: (${{nodeData.x}}px, ${{nodeData.y}}px).`);
      }} else {{
        inspectorController.bindEntity(null);
        narrativeController.update('Deselected all nodes. Showing workspace overview.');
      }}
    }},
    onNodeMove: (nodeId, x, y) => {{
      const fallback = document.getElementById('field-x') || document.getElementById('field-position');
      if (fallback) fallback.textContent = `(${{Math.round(x)}}, ${{Math.round(y)}})`;
    }}
  }});

  // Button hooks
  const btnUndo = document.getElementById('btn-undo');
  if (btnUndo) btnUndo.addEventListener('click', executeUndo);

  const btnRedo = document.getElementById('btn-redo');
  if (btnRedo) btnRedo.addEventListener('click', executeRedo);

  const btnReset = document.getElementById('btn-reset-view');
  if (btnReset) btnReset.addEventListener('click', () => {{
    canvasController.resetViewport();
    narrativeController.update('Reset spatial viewport matrix to origin (0, 0) at 100% scale.');
  }});

  // 2. Human Ergonomics Keyboard Hotkeys Contract
  let isPlaying = false;
  const btnPlay = document.getElementById('btn-play-pause');

  function togglePlayback() {{
    isPlaying = !isPlaying;
    if (btnPlay) btnPlay.textContent = isPlaying ? '⏸ Pause' : '▶ Play';
    narrativeController.update(isPlaying ? 'Simulation playback started.' : 'Simulation playback paused.');
  }}

  if (btnPlay) btnPlay.addEventListener('click', togglePlayback);

  window.addEventListener('keydown', (e) => {{
    // Skip hotkeys if focused on input or textarea
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) return;

    // Hotkey: Undo (Cmd+Z or Ctrl+Z) / Redo (Cmd+Y, Ctrl+Y, Cmd+Shift+Z)
    const isUndo = {str(ergo.enable_undo_hotkeys).lower()} && (e.metaKey || e.ctrlKey) && (e.key === 'z' || e.key === 'Z') && !e.shiftKey;
    const isRedo = {str(ergo.enable_undo_hotkeys).lower()} && ((e.metaKey || e.ctrlKey) && (e.key === 'y' || e.key === 'Y' || ((e.key === 'z' || e.key === 'Z') && e.shiftKey)));

    if (isUndo) {{
      e.preventDefault();
      executeUndo();
      return;
    }}

    if (isRedo) {{
      e.preventDefault();
      executeRedo();
      return;
    }}

    // Hotkey: Escape to deselect
    if ({str(ergo.enable_escape_deselect).lower()} && e.key === 'Escape') {{
      e.preventDefault();
      canvasController.deselectAll();
      return;
    }}

    // Hotkey: Space to toggle playback
    if ({str(ergo.enable_space_playback).lower()} && (e.key === ' ' || e.code === 'Space')) {{
      e.preventDefault();
      togglePlayback();
      return;
    }}
  }});

  // Initial Checkpoint
  pushState('Initialization', {{ nodes: 2, timestamp: Date.now() }});
}});
"""

    def scaffold_studio(self, contract: UIContractSpecification) -> Dict[str, str]:
        """Scaffolds complete in-memory Tactile Studio assets adhering to the contract."""
        contract.validate()

        html_content = self.generate_html(contract)
        css_content = StudioCSSTemplate.render_css(contract.archetype)
        js_content = self.generate_js(contract)

        bundle = {
            "index.html": html_content,
            "style.css": css_content,
            "app.js": js_content,
        }

        # Statically verify zero-CDN compliance [HERM-005]
        self._verify_zero_cdn_compliance(bundle)
        return bundle

    def scaffold_to_dir(
        self,
        contract: UIContractSpecification,
        target_dir: Path | str,
    ) -> Dict[str, Path]:
        """Scaffolds and physically writes complete Tactile Studio files to target directory."""
        bundle = self.scaffold_studio(contract)
        out_dir = Path(target_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        emitted_paths: Dict[str, Path] = {}
        for filename, content in bundle.items():
            file_path = out_dir / filename
            file_path.write_text(content, encoding="utf-8")
            emitted_paths[filename] = file_path

        return emitted_paths
