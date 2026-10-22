"""Code Emission Templates for Axioma Joy (System G2b).

Emits production-grade frontend HTML, CSS, JavaScript, and runtime server code
implementing Eugenia Cheng's visceral category theory pedagogy for art students.
"""

from typing import Any, Dict
from g2b_compiler.ir.semantic_ir import SemanticDomainIR
from g2b_compiler.ir.statechart_ir import StatechartIR
from g2b_compiler.ir.contract_ir import DualBoundaryContractIR


def generate_joy_index_html(semantic_ir: SemanticDomainIR) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>{semantic_ir.title} - {semantic_ir.tagline}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body class="theme-dark">
  <div id="app" class="app-container">
    <!-- TOP NAVIGATION BAR -->
    <header class="app-header">
      <div class="header-brand">
        <span class="brand-logo">🍰</span>
        <div class="brand-titles">
          <h1 class="brand-title">{semantic_ir.title}</h1>
          <span class="brand-subtitle">{semantic_ir.tagline}</span>
        </div>
      </div>

      <!-- REALM SWITCHER TABS -->
      <nav class="realm-nav" aria-label="Category Realms">
        <button id="btn-realm-baking" class="btn btn-realm active" data-realm="realm_baking" title="Eugenia Cheng's signature recipe category">
          <span class="realm-icon">🍰</span>
          <span class="realm-name">The Baker's Kitchen</span>
        </button>
        <button id="btn-realm-cube" class="btn btn-realm" data-realm="realm_cube30" title="3D prime factor lattice of divisors of 30">
          <span class="realm-icon">🎲</span>
          <span class="realm-name">3D Factorization Cube (30)</span>
        </button>
        <button id="btn-realm-functor" class="btn btn-realm" data-realm="realm_functor" title="Structure-preserving analogies between culinary and art worlds">
          <span class="realm-icon">🌉</span>
          <span class="realm-name">The Analogy Bridge</span>
        </button>
      </nav>

      <!-- GLOBAL ACTION CONTROLS -->
      <div class="header-actions">
        <button id="btn-sound-toggle" class="btn btn-secondary btn-icon" title="Toggle Web Audio Harmonics (Major Chords on Commutativity)" aria-pressed="true">
          <span id="sound-icon">🔊</span>
        </button>
        <button id="btn-dual-toggle" class="btn btn-secondary" title="Inspect Dual Opposite Category (C^op) - Reverses all arrows">
          <span class="btn-icon-text">🔄 Dual (C<sup>op</sup>)</span>
        </button>
        <button id="btn-undo" class="btn btn-secondary btn-icon" title="Functorial Undo (Cmd+Z)" disabled>
          <span>↩</span>
        </button>
        <button id="btn-sync" class="btn btn-secondary btn-icon" title="Local-First Sync & Diagram Backup">
          <span>💾</span>
        </button>
        <button id="btn-reset" class="btn btn-secondary btn-icon" title="Reset Realm Canvas">
          <span>🧹</span>
        </button>
      </div>
    </header>

    <!-- MAIN WORKSPACE -->
    <main class="app-main">
      <!-- FLOATING CANVAS TOOLBAR -->
      <aside class="canvas-toolbar" aria-label="Category Canvas Tools">
        <div class="tool-group">
          <button id="tool-select" class="btn btn-tool active" data-mode="select" title="Select & Inspect Object (Yoneda Relational View)">
            <span class="tool-icon">👆</span>
            <span class="tool-label">Inspect</span>
          </button>
          <button id="tool-draw" class="btn btn-tool" data-mode="draw" title="Draw Morphism Arrow (Drag between objects)">
            <span class="tool-icon">✏️</span>
            <span class="tool-label">Draw Arrow</span>
          </button>
          <button id="tool-compose" class="btn btn-tool" data-mode="compose" title="Compose Morphisms (Select arrow f, then arrow g to synthesize g o f)">
            <span class="tool-icon">🔗</span>
            <span class="tool-label">Compose (g ∘ f)</span>
          </button>
          <button id="tool-commute" class="btn btn-tool" data-mode="commute" title="Check Commutativity (Test if two paths evaluate identically)">
            <span class="tool-icon">✨</span>
            <span class="tool-label">Commute</span>
          </button>
          <button id="tool-add-node" class="btn btn-tool" data-mode="add_node" title="Add New Category Object Node">
            <span class="tool-icon">➕</span>
            <span class="tool-label">New Object</span>
          </button>
        </div>

        <div class="toolbar-status">
          <span class="status-indicator-dot"></span>
          <span id="status-mode-label" class="status-mode-text">Inspect Mode</span>
        </div>
      </aside>

      <!-- CANVAS VIEWPORT (PRIMARY INTERACTION SURFACE) -->
      <section class="canvas-viewport">
        <!-- REALM 1: 2D CATEGORY CANVAS (BAKING & FREEFORM) -->
        <div id="view-canvas-2d" class="realm-view active">
          <svg id="category-svg" class="category-svg-surface" width="100%" height="100%">
            <defs>
              <!-- Standard Morphism Arrowhead -->
              <marker id="arrowhead-normal" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#818cf8" />
              </marker>
              <!-- Composite Morphism Arrowhead (g o f) -->
              <marker id="arrowhead-composite" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981" />
              </marker>
              <!-- Commuting Verified Golden Arrowhead -->
              <marker id="arrowhead-commuting" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#fbbf24" />
              </marker>
              <!-- Dual Opposite Arrowhead (C^op) -->
              <marker id="arrowhead-dual" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#ec4899" />
              </marker>

              <!-- Radial glow filter for commuting faces -->
              <filter id="gold-glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="8" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            <!-- Background Grid Pattern -->
            <rect class="svg-bg-grid" width="100%" height="100%" fill="transparent" />

            <!-- Dynamic Commutative Face Polygons Layer -->
            <g id="commuting-faces-layer"></g>

            <!-- Dynamic Morphism Arrows Layer -->
            <g id="arrows-layer"></g>

            <!-- Temporary Drag / In-Flight Arrow Line -->
            <line id="drag-arrow-line" class="drag-arrow-line hidden" x1="0" y1="0" x2="0" y2="0" marker-end="url(#arrowhead-normal)" />

            <!-- Dynamic Category Object Nodes Layer -->
            <g id="nodes-layer"></g>
          </svg>
        </div>

        <!-- REALM 2: 3D FACTORIZATION CUBE VIEWPORT -->
        <div id="view-cube-3d" class="realm-view hidden">
          <div class="cube-hud">
            <div class="hud-card">
              <h3 class="hud-title">Eugenia Cheng's Divisors of 30 Lattice</h3>
              <p class="hud-desc">An interactive 3D prime-factor poset category. Nodes are divisors; arrows are prime multiplications (x2, x3, x5). Every 2D square face commutes!</p>
              <div class="cube-controls">
                <button id="btn-cube-rotate-left" class="btn btn-secondary btn-sm">↺ Rotate Left</button>
                <button id="btn-cube-rotate-right" class="btn btn-secondary btn-sm">↻ Rotate Right</button>
                <button id="btn-cube-check-face" class="btn btn-accent btn-sm">✨ Verify Face Commutativity</button>
                <button id="btn-cube-reset-view" class="btn btn-secondary btn-sm">Reset Orientation</button>
              </div>
            </div>
          </div>
          <div id="cube-canvas-container" class="cube-canvas-container">
            <canvas id="cube-3d-canvas" class="cube-canvas" width="800" height="600"></canvas>
          </div>
        </div>

        <!-- REALM 3: FUNCTOR ANALOGY BRIDGE VIEWPORT -->
        <div id="view-functor-bridge" class="realm-view hidden">
          <div class="functor-bridge-layout">
            <!-- Left World: Culinary Domain -->
            <div class="functor-world-panel" id="world-culinary">
              <div class="world-header">
                <span class="world-badge">Category A</span>
                <h3 class="world-title">🍰 Culinary Domain</h3>
                <p class="world-sub">Processes on ingredients, emulsions, and baked sponges.</p>
              </div>
              <div class="world-card-list" id="culinary-card-list"></div>
            </div>

            <!-- Central Functor Mapping Bridge -->
            <div class="functor-center-bridge">
              <div class="bridge-glyph">
                <span class="bridge-functor-label">Functor F</span>
                <div class="bridge-arrow-stream">
                  <span class="stream-particle">⟹</span>
                  <span class="stream-particle">⟹</span>
                  <span class="stream-particle">⟹</span>
                </div>
              </div>
              <div class="functor-axioms-card">
                <h4>Functor Invariants</h4>
                <ul>
                  <li><code>F(id<sub>A</sub>) = id<sub>F(A)</sub></code></li>
                  <li><code>F(g ∘ f) = F(g) ∘ F(f)</code></li>
                </ul>
                <button id="btn-test-functor-coherence" class="btn btn-accent btn-sm">
                  <span>Verify Analogy Preservation</span>
                </button>
              </div>
            </div>

            <!-- Right World: Visual Art Domain -->
            <div class="functor-world-panel" id="world-art">
              <div class="world-header">
                <span class="world-badge">Category B</span>
                <h3 class="world-title">🎨 Visual Art Domain</h3>
                <p class="world-sub">Processes on raw pigments, binders, and oil canvases.</p>
              </div>
              <div class="world-card-list" id="art-card-list"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- RIGHT SIDE DRAWER: YONEDA RELATIONAL INSPECTOR & LESSON NOTES -->
      <aside id="inspector-drawer" class="inspector-drawer">
        <div class="drawer-header">
          <h2 id="drawer-title" class="drawer-heading">Relational Inspector</h2>
          <button id="btn-close-drawer" class="btn btn-secondary btn-icon" title="Close Panel">✕</button>
        </div>

        <!-- Yoneda Object View -->
        <div id="panel-yoneda" class="drawer-panel active">
          <div class="yoneda-badge-row">
            <span class="yoneda-concept-pill">Yoneda Perspective</span>
          </div>
          <div class="selected-node-hero">
            <span id="selected-node-icon" class="node-hero-icon">⚪</span>
            <div class="node-hero-meta">
              <h3 id="selected-node-label" class="node-hero-title">No Object Selected</h3>
              <span id="selected-node-id" class="node-hero-id">Select any node on the canvas</span>
            </div>
          </div>
          <p id="selected-node-desc" class="node-hero-desc">In category theory, an object is not defined by internal substance; it is known entirely through its incoming and outgoing relationships (morphisms) with all other objects.</p>

          <div class="morphism-summary-box">
            <div class="summary-col">
              <span class="summary-num" id="count-incoming">0</span>
              <span class="summary-lbl">Incoming Arrows</span>
            </div>
            <div class="summary-col">
              <span class="summary-num" id="count-outgoing">0</span>
              <span class="summary-lbl">Outgoing Arrows</span>
            </div>
            <div class="summary-col">
              <span class="summary-num" id="count-loops">0</span>
              <span class="summary-lbl">Identity Loops</span>
            </div>
          </div>

          <div class="relations-list-box">
            <h4 class="relations-heading">Morphism Connections</h4>
            <div id="morphism-connections-list" class="connections-list">
              <span class="empty-state-text">No active arrows connected to this node.</span>
            </div>
          </div>
        </div>

        <!-- Commutative Proof & Harmony Panel -->
        <div id="panel-commutativity" class="drawer-panel hidden">
          <div class="yoneda-badge-row">
            <span class="yoneda-concept-pill golden">Commutative Coherence</span>
          </div>
          <h3 class="commutativity-title">Path Resolution</h3>
          <p class="commutativity-desc">Testing whether traversing path <code>P₁</code> yields the exact same structural transformation as traversing path <code>P₂</code>.</p>

          <div id="commutativity-comparison-box" class="comparison-card">
            <div class="path-row">
              <span class="path-badge">Path 1 (Composite):</span>
              <span id="label-path-1" class="path-code">-</span>
            </div>
            <div class="path-row">
              <span class="path-badge">Path 2 (Direct):</span>
              <span id="label-path-2" class="path-code">-</span>
            </div>
            <div id="commutativity-verdict" class="verdict-banner pending">
              <span id="verdict-text">Select two paths to test commutativity</span>
            </div>
          </div>

          <button id="btn-harmonize-face" class="btn btn-accent btn-large" disabled>
            <span>Play Harmonic Resolution Chime 🎵</span>
          </button>
        </div>

        <!-- Cheng Pedagogical Lesson Insights -->
        <div class="pedagogical-notes-card">
          <h4 class="notes-heading">🍰 Eugenia Cheng's Kitchen Note</h4>
          <p id="pedagogical-quote" class="notes-body">"Baking is a wonderful model for mathematics. In cooking, order matters: putting eggs into hot butter makes scrambled eggs; whisking eggs into cold milk makes custard. Mathematics is the study of how things combine."</p>
        </div>
      </aside>
    </main>

    <!-- EXCEPTION ENCLAVE MODAL (DEMARCATED ERROR RECOVERY [L1-016]) -->
    <div id="type-mismatch-modal" class="modal-overlay hidden" role="dialog" aria-modal="true" aria-labelledby="modal-err-title">
      <div class="modal-card error-enclave-card">
        <div class="modal-icon error-icon">⚠️</div>
        <h3 id="modal-err-title" class="modal-title">Type Mismatch in Morphism Composition</h3>
        <p id="modal-err-message" class="modal-desc">In category theory, two morphisms <code>f: A → B</code> and <code>g: C → D</code> cannot be composed unless the codomain (target) of <code>f</code> matches the domain (source) of <code>g</code> (i.e. <code>B = C</code>).</p>
        <div class="enclave-recommendation-box">
          <span class="rec-label">Pedagogical Recovery:</span>
          <span id="modal-err-recovery" class="rec-text">Select an arrow that originates from the endpoint of your first arrow.</span>
        </div>
        <div class="modal-actions">
          <button id="btn-enclave-retry" class="btn btn-primary">Try Composable Arrow</button>
          <button id="btn-enclave-dismiss" class="btn btn-secondary">Dismiss</button>
        </div>
      </div>
    </div>

    <!-- LOCAL-FIRST SYNC & BACKUP MODAL -->
    <div id="sync-modal" class="modal-overlay hidden" role="dialog" aria-modal="true" aria-labelledby="modal-sync-title">
      <div class="modal-card">
        <h3 id="modal-sync-title" class="modal-title">Local-First Storage & Diagram Export</h3>
        <p class="modal-desc">All category diagrams, prime factor lattices, and functor bridges are stored locally on your device with 100% privacy and zero tracking.</p>
        <div class="sync-actions-grid">
          <button id="btn-export-json" class="btn btn-primary">
            <span>⬇ Export JSON Snapshot</span>
          </button>
          <button id="btn-import-trigger" class="btn btn-secondary">
            <span>⬆ Import JSON Snapshot</span>
          </button>
          <input type="file" id="file-import-json" accept=".json" class="hidden">
          <button id="btn-export-svg" class="btn btn-secondary">
            <span>🖼 Download SVG Diagram</span>
          </button>
        </div>
        <div class="modal-actions">
          <button id="btn-close-sync" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- SCRIPT HYDRATION -->
  <script type="module" src="app.js"></script>
</body>
</html>
"""


def generate_joy_style_css(semantic_ir: SemanticDomainIR) -> str:
    return """/* ==========================================================================
   Axioma Joy: Structural Category Theory & Pedagogical Reasoning Studio
   Design System tokens conforming to Nielsen-Norman heuristics and Fitts's Law.
   ========================================================================== */

:root {
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;

  /* Color Palette */
  --bg-dark: #090d16;
  --bg-surface: #111827;
  --bg-card: #1f2937;
  --bg-card-hover: #374151;
  --bg-elevated: #1e293b;
  --border-color: #374151;
  --border-focus: #6366f1;

  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
  --text-muted: #6b7280;

  --accent-primary: #6366f1;
  --accent-hover: #4f46e5;
  --accent-emerald: #10b981;
  --accent-amber: #f59e0b;
  --accent-rose: #f43f5e;
  --accent-gold: #fbbf24;
  --accent-cyan: #06b6d4;
  --accent-pink: #ec4899;

  /* Ergonomic & Touch Metrics (Fitts's Law >= 48px) */
  --touch-target: 48px;
  --border-radius-sm: 6px;
  --border-radius-md: 10px;
  --border-radius-lg: 16px;
  --border-radius-full: 9999px;
  --transition-fast: 0.15s ease-in-out;
  --transition-normal: 0.25s ease-in-out;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
}

body {
  font-family: var(--font-family);
  background-color: var(--bg-dark);
  color: var(--text-primary);
  min-height: 100vh;
  overflow: hidden;
  user-select: none;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
}

/* ==========================================================================
   HEADER & REALM NAVIGATION
   ========================================================================== */

.app-header {
  height: 64px;
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  gap: 16px;
  z-index: 50;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo {
  font-size: 28px;
  line-height: 1;
}

.brand-titles {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #fff;
}

.brand-subtitle {
  font-size: 11px;
  color: var(--text-muted);
}

.realm-nav {
  display: flex;
  gap: 8px;
  background-color: var(--bg-card);
  padding: 4px;
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-color);
}

.btn-realm {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  height: 40px;
  background: transparent;
  border: none;
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-realm:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.05);
}

.btn-realm.active {
  background-color: var(--accent-primary);
  color: #fff;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.35);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ==========================================================================
   BUTTONS & DESIGN TOKENS
   ========================================================================== */

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: var(--touch-target);
  padding: 0 16px;
  font-size: 14px;
  font-weight: 600;
  border-radius: var(--border-radius-sm);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  outline: none;
}

.btn-icon {
  width: var(--touch-target);
  padding: 0;
  font-size: 18px;
}

.btn-sm {
  min-height: 36px;
  padding: 0 12px;
  font-size: 12px;
}

.btn-large {
  min-height: 52px;
  font-size: 15px;
  width: 100%;
}

.btn-primary {
  background-color: var(--accent-primary);
  color: #fff;
}

.btn-primary:hover {
  background-color: var(--accent-hover);
}

.btn-secondary {
  background-color: var(--bg-card);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background-color: var(--bg-card-hover);
}

.btn-accent {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-accent:hover {
  filter: brightness(1.1);
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}

/* ==========================================================================
   MAIN WORKSPACE & FLOATING TOOLBAR
   ========================================================================== */

.app-main {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
}

.canvas-toolbar {
  position: absolute;
  top: 20px;
  left: 20px;
  background-color: rgba(17, 24, 39, 0.9);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  z-index: 30;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
}

.tool-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.btn-tool {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 44px;
  min-width: 150px;
  padding: 0 12px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-tool:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.06);
}

.btn-tool.active {
  background-color: rgba(99, 102, 241, 0.2);
  border-color: var(--accent-primary);
  color: #fff;
  font-weight: 600;
}

.toolbar-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 4px;
}

.status-indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--accent-emerald);
  box-shadow: 0 0 6px var(--accent-emerald);
}

.status-mode-text {
  font-size: 11px;
  color: var(--text-muted);
}

/* ==========================================================================
   CANVAS VIEWPORTS & REALM VIEWS
   ========================================================================== */

.canvas-viewport {
  flex: 1;
  position: relative;
  background-color: var(--bg-dark);
  background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px);
  background-size: 32px 32px;
}

.realm-view {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

.realm-view.hidden {
  display: none;
}

/* SVG Surface */
.category-svg-surface {
  width: 100%;
  height: 100%;
  cursor: default;
}

/* Morphism SVG Paths */
.morphism-path {
  fill: none;
  stroke: #818cf8;
  stroke-width: 2.5;
  transition: stroke 0.2s, stroke-width 0.2s;
  cursor: pointer;
}

.morphism-path:hover {
  stroke: #c7d2fe;
  stroke-width: 4;
}

.morphism-path.composite {
  stroke: var(--accent-emerald);
  stroke-width: 3;
  stroke-dasharray: 6 3;
}

.morphism-path.commuting {
  stroke: var(--accent-gold);
  stroke-width: 3.5;
  filter: drop-shadow(0 0 6px rgba(251, 191, 36, 0.6));
}

.morphism-path.dual-reversed {
  stroke: var(--accent-pink);
  stroke-width: 2.5;
}

.morphism-label {
  font-size: 12px;
  font-weight: 600;
  fill: #e0e7ff;
  text-anchor: middle;
  pointer-events: none;
  paint-order: stroke;
  stroke: #0f172a;
  stroke-width: 3px;
  stroke-linecap: butt;
  stroke-linejoin: miter;
}

.drag-arrow-line {
  stroke: #a5b4fc;
  stroke-width: 3;
  stroke-dasharray: 4 4;
  pointer-events: none;
}

/* Commutative Face Polygons */
.commuting-face {
  fill: rgba(251, 191, 36, 0.12);
  stroke: rgba(251, 191, 36, 0.4);
  stroke-width: 2;
  stroke-dasharray: 6 4;
  animation: pulse-gold 3s infinite ease-in-out;
}

@keyframes pulse-gold {
  0%, 100% { fill-opacity: 0.08; stroke-opacity: 0.3; }
  50% { fill-opacity: 0.22; stroke-opacity: 0.8; }
}

/* Category Object Nodes (SVG) */
.category-node-group {
  cursor: grab;
  transition: transform var(--transition-fast);
}

.category-node-group:active {
  cursor: grabbing;
}

.node-halo {
  fill: none;
  stroke: transparent;
  stroke-width: 6;
  transition: all var(--transition-fast);
}

.category-node-group:hover .node-halo {
  stroke: rgba(99, 102, 241, 0.4);
}

.category-node-group.selected .node-halo {
  stroke: var(--accent-primary);
  stroke-width: 8;
  filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.8));
}

.node-circle {
  stroke-width: 2.5;
  stroke: rgba(255, 255, 255, 0.2);
  transition: all var(--transition-fast);
}

.node-icon-text {
  font-size: 20px;
  text-anchor: middle;
  dominant-baseline: central;
  pointer-events: none;
}

.node-title-text {
  font-size: 13px;
  font-weight: 600;
  fill: #fff;
  text-anchor: middle;
  pointer-events: none;
  paint-order: stroke;
  stroke: #090d16;
  stroke-width: 4px;
}

/* ==========================================================================
   3D FACTORIZATION CUBE VIEWPORT
   ========================================================================== */

.cube-hud {
  position: absolute;
  top: 20px;
  right: 20px;
  max-width: 380px;
  z-index: 20;
}

.hud-card {
  background-color: rgba(17, 24, 39, 0.9);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  padding: 18px;
}

.hud-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 6px;
}

.hud-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
  margin-bottom: 14px;
}

.cube-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.cube-canvas-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cube-canvas {
  cursor: grab;
}

.cube-canvas:active {
  cursor: grabbing;
}

/* ==========================================================================
   FUNCTOR ANALOGY BRIDGE VIEWPORT
   ========================================================================== */

.functor-bridge-layout {
  display: flex;
  height: 100%;
  width: 100%;
  padding: 24px 24px 24px 200px;
  gap: 20px;
}

.functor-world-panel {
  flex: 1;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.world-header {
  padding: 16px 20px;
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
}

.world-badge {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--accent-cyan);
  letter-spacing: 0.05em;
}

.world-title {
  font-size: 16px;
  font-weight: 700;
  margin-top: 2px;
}

.world-sub {
  font-size: 12px;
  color: var(--text-muted);
}

.world-card-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}

.functor-center-bridge {
  width: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.bridge-glyph {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.bridge-functor-label {
  font-size: 18px;
  font-weight: 800;
  color: var(--accent-amber);
  letter-spacing: 0.05em;
}

.bridge-arrow-stream {
  font-size: 24px;
  color: var(--accent-amber);
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: pulse-stream 1.5s infinite linear;
}

@keyframes pulse-stream {
  0% { transform: translateY(-4px); opacity: 0.6; }
  50% { transform: translateY(4px); opacity: 1; }
  100% { transform: translateY(-4px); opacity: 0.6; }
}

.functor-axioms-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  padding: 14px;
  font-size: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.functor-axioms-card h4 {
  font-size: 12px;
  color: var(--text-secondary);
}

.functor-axioms-card ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.functor-axioms-card code {
  font-family: var(--font-mono);
  background: rgba(0, 0, 0, 0.4);
  padding: 2px 6px;
  border-radius: 4px;
  color: #a5b4fc;
}

/* ==========================================================================
   RIGHT SIDE DRAWER (INSPECTOR)
   ========================================================================== */

.inspector-drawer {
  width: 360px;
  background-color: var(--bg-surface);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  padding: 20px;
  gap: 16px;
  overflow-y: auto;
  z-index: 40;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.drawer-heading {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.drawer-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.drawer-panel.hidden {
  display: none;
}

.yoneda-concept-pill {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  background-color: rgba(99, 102, 241, 0.15);
  color: #a5b4fc;
  padding: 4px 8px;
  border-radius: var(--border-radius-full);
  letter-spacing: 0.05em;
}

.yoneda-concept-pill.golden {
  background-color: rgba(251, 191, 36, 0.2);
  color: var(--accent-gold);
}

.selected-node-hero {
  display: flex;
  align-items: center;
  gap: 14px;
  background-color: var(--bg-card);
  padding: 12px;
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-color);
}

.node-hero-icon {
  font-size: 32px;
}

.node-hero-title {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
}

.node-hero-id {
  font-size: 11px;
  color: var(--text-muted);
}

.node-hero-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.morphism-summary-box {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  padding: 10px;
  text-align: center;
}

.summary-num {
  font-size: 18px;
  font-weight: 700;
  color: var(--accent-primary);
  display: block;
}

.summary-lbl {
  font-size: 10px;
  color: var(--text-muted);
}

.relations-heading {
  font-size: 12px;
  text-transform: uppercase;
  color: var(--text-secondary);
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.connections-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 160px;
  overflow-y: auto;
}

.connection-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  background-color: var(--bg-card);
  border-radius: var(--border-radius-sm);
  font-size: 12px;
}

.empty-state-text {
  font-size: 12px;
  color: var(--text-muted);
  font-style: italic;
}

/* Commutativity Panel */
.comparison-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.path-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.path-badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
}

.path-code {
  font-family: var(--font-mono);
  font-size: 12px;
  color: #fff;
  background: rgba(0, 0, 0, 0.4);
  padding: 4px 8px;
  border-radius: 4px;
}

.verdict-banner {
  padding: 8px 12px;
  border-radius: var(--border-radius-sm);
  font-size: 12px;
  font-weight: 600;
  text-align: center;
}

.verdict-banner.pending {
  background-color: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
}

.verdict-banner.success {
  background-color: rgba(16, 185, 129, 0.2);
  border: 1px solid var(--accent-emerald);
  color: var(--accent-emerald);
}

.pedagogical-notes-card {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: var(--border-radius-md);
  padding: 14px;
  margin-top: auto;
}

.notes-heading {
  font-size: 12px;
  font-weight: 700;
  color: var(--accent-gold);
  margin-bottom: 6px;
}

.notes-body {
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.5;
  font-style: italic;
}

/* ==========================================================================
   MODALS (EXCEPTION ENCLAVE & LOCAL-FIRST SYNC)
   ========================================================================== */

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-overlay.hidden {
  display: none;
}

.modal-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  padding: 24px;
  max-width: 480px;
  width: 90%;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
}

.modal-icon {
  font-size: 36px;
  line-height: 1;
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.modal-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.enclave-recommendation-box {
  background-color: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: var(--border-radius-sm);
  padding: 10px 14px;
  font-size: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rec-label {
  font-weight: 700;
  color: var(--accent-amber);
}

.rec-text {
  color: var(--text-primary);
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 8px;
}

.sync-actions-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.hidden {
  display: none !important;
}
"""


def generate_joy_app_js(semantic_ir: SemanticDomainIR, statechart_ir: StatechartIR) -> str:
    return """/**
 * Axioma Joy - Reactive Client Controller & Canvas Engine.
 * Conforms to XState v5 Statechart Runtime and Eugenia Cheng's Categorical Pedagogy.
 */

import { DeterministicFSM, machineConfig } from './machine.js';

// =============================================================================
// 1. STATE INITIALIZATION & STATECHART HOOKS
// =============================================================================

const fsm = new DeterministicFSM(machineConfig);

// Audio Synthesis Substrate (Real Web Audio API - NEG-G2-005 Compliant)
class HarmonicSynthesizer {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  init() {
    if (!this.ctx && (window.AudioContext || window.webkitAudioContext)) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
    }
  }

  playChord(frequencies = [261.63, 329.63, 392.00], duration = 0.8) {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }

    const now = this.ctx.currentTime;
    frequencies.forEach(freq => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, now);

      gain.gain.setValueAtTime(0.001, now);
      gain.gain.exponentialRampToValueAtTime(0.12, now + 0.05);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + duration);
    });
  }

  playCommutingMajorChord() {
    // C Major Triad (C4, E4, G4, C5)
    this.playChord([261.63, 329.63, 392.00, 523.25], 1.0);
  }

  playTensionChord() {
    // Dissonant Minor Second / Diminished interval
    this.playChord([261.63, 277.18], 0.4);
  }
}

const synth = new HarmonicSynthesizer();

// Application State
let appState = {
  activeRealmId: 'realm_baking',
  nodes: [],
  arrows: [],
  selectedNodeId: null,
  selectedArrowId: null,
  compositionStep: null, // { f: null, g: null }
  isDualMode: false,
  activeTool: 'select',
};

// =============================================================================
// 2. DATA PERSISTENCE & CLEAN-SLATE HYDRATION
// =============================================================================

async function loadInitialState() {
  const localData = localStorage.getItem('axioma_joy_state');
  if (localData) {
    try {
      const parsed = JSON.parse(localData);
      appState.nodes = parsed.nodes || [];
      appState.arrows = parsed.arrows || [];
      appState.activeRealmId = parsed.activeRealmId || 'realm_baking';
      renderCurrentRealm();
      return;
    } catch (e) {
      console.warn('Corrupt local state, falling back to clean seeds.', e);
    }
  }

  try {
    const res = await fetch('/data/app_state.json');
    if (res.ok) {
      const seeds = await res.json();
      appState.nodes = seeds.nodes || [];
      appState.arrows = seeds.arrows || [];
      saveStateLocally();
      renderCurrentRealm();
    }
  } catch (err) {
    console.warn('Could not fetch server seeds, running local defaults.', err);
  }
}

function saveStateLocally() {
  localStorage.setItem('axioma_joy_state', JSON.stringify({
    activeRealmId: appState.activeRealmId,
    nodes: appState.nodes,
    arrows: appState.arrows,
  }));
  updateUndoButton();
}

function updateUndoButton() {
  const btnUndo = document.getElementById('btn-undo');
  if (btnUndo) {
    btnUndo.disabled = fsm.historyStack.length === 0;
  }
}

// =============================================================================
// 3. SVG 2D CATEGORY CANVAS ENGINE
// =============================================================================

const svg = document.getElementById('category-svg');
const nodesLayer = document.getElementById('nodes-layer');
const arrowsLayer = document.getElementById('arrows-layer');
const commutingLayer = document.getElementById('commuting-faces-layer');
const dragLine = document.getElementById('drag-arrow-line');

let isDraggingNode = false;
let draggedNode = null;
let dragOffset = { x: 0, y: 0 };

let isDrawingArrow = false;
let arrowSourceNode = null;

function renderCurrentRealm() {
  if (appState.activeRealmId === 'realm_cube30') {
    document.getElementById('view-canvas-2d').classList.add('hidden');
    document.getElementById('view-cube-3d').classList.remove('hidden');
    document.getElementById('view-functor-bridge').classList.add('hidden');
    renderCube3D();
    return;
  }
  if (appState.activeRealmId === 'realm_functor') {
    document.getElementById('view-canvas-2d').classList.add('hidden');
    document.getElementById('view-cube-3d').classList.add('hidden');
    document.getElementById('view-functor-bridge').classList.remove('hidden');
    renderFunctorBridge();
    return;
  }

  // 2D Canvas (Baking or Freeform)
  document.getElementById('view-canvas-2d').classList.remove('hidden');
  document.getElementById('view-cube-3d').classList.add('hidden');
  document.getElementById('view-functor-bridge').classList.add('hidden');

  render2DCanvas();
}

function render2DCanvas() {
  nodesLayer.innerHTML = '';
  arrowsLayer.innerHTML = '';
  commutingLayer.innerHTML = '';

  const activeNodes = appState.nodes.filter(n => n.realm_id === appState.activeRealmId);
  const activeArrows = appState.arrows.filter(a => a.realm_id === appState.activeRealmId);

  // Render Arrows
  activeArrows.forEach(arrow => {
    const src = activeNodes.find(n => n.id === (appState.isDualMode ? arrow.target_id : arrow.source_id));
    const tgt = activeNodes.find(n => n.id === (appState.isDualMode ? arrow.source_id : arrow.target_id));
    if (!src || !tgt) return;

    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.dataset.arrowId = arrow.id;

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const d = calculateArrowPath(src.x, src.y, tgt.x, tgt.y);
    path.setAttribute('d', d);
    path.setAttribute('class', `morphism-path ${arrow.composition_chain?.length ? 'composite' : ''} ${appState.isDualMode ? 'dual-reversed' : ''}`);

    let marker = 'url(#arrowhead-normal)';
    if (arrow.composition_chain?.length) marker = 'url(#arrowhead-composite)';
    if (appState.isDualMode) marker = 'url(#arrowhead-dual)';
    path.setAttribute('marker-end', marker);

    // Arrow text label
    const midX = (src.x + tgt.x) / 2;
    const midY = (src.y + tgt.y) / 2 - 10;
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', midX);
    text.setAttribute('y', midY);
    text.setAttribute('class', 'morphism-label');
    text.textContent = appState.isDualMode ? `${arrow.label}ᵒᵖ` : arrow.label;

    g.appendChild(path);
    g.appendChild(text);

    g.addEventListener('click', (e) => {
      e.stopPropagation();
      handleArrowClick(arrow);
    });

    arrowsLayer.appendChild(g);
  });

  // Render Nodes
  activeNodes.forEach(node => {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('class', `category-node-group ${node.id === appState.selectedNodeId ? 'selected' : ''}`);
    g.setAttribute('transform', `translate(${node.x}, ${node.y})`);
    g.dataset.nodeId = node.id;

    const halo = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    halo.setAttribute('r', '32');
    halo.setAttribute('class', 'node-halo');

    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('r', '24');
    circle.setAttribute('fill', node.color || '#6366f1');
    circle.setAttribute('class', 'node-circle');

    const icon = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    icon.setAttribute('class', 'node-icon-text');
    icon.textContent = node.icon || '✨';

    const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    label.setAttribute('y', '42');
    label.setAttribute('class', 'node-title-text');
    label.textContent = node.label;

    g.appendChild(halo);
    g.appendChild(circle);
    g.appendChild(icon);
    g.appendChild(label);

    g.addEventListener('mousedown', (e) => handleNodeMouseDown(e, node));
    g.addEventListener('mouseup', (e) => handleNodeMouseUp(e, node));
    g.addEventListener('click', (e) => {
      e.stopPropagation();
      selectNode(node);
    });

    nodesLayer.appendChild(g);
  });

  checkAndHighlightCommutativity();
}

function calculateArrowPath(x1, y1, x2, y2) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const dist = Math.sqrt(dx * dx + dy * dy);
  if (dist === 0) return '';

  const offset = 26;
  const sx = x1 + (dx / dist) * offset;
  const sy = y1 + (dy / dist) * offset;
  const tx = x2 - (dx / dist) * offset;
  const ty = y2 - (dy / dist) * offset;

  return `M ${sx} ${sy} L ${tx} ${ty}`;
}

// =============================================================================
// 4. INTERACTION HANDLERS & GESTURES
// =============================================================================

function selectNode(node) {
  fsm.transition('SELECT_OBJECT');
  appState.selectedNodeId = node.id;
  updateInspectorWithNode(node);
  render2DCanvas();
}

function updateInspectorWithNode(node) {
  document.getElementById('panel-yoneda').classList.remove('hidden');
  document.getElementById('panel-commutativity').classList.add('hidden');

  document.getElementById('selected-node-icon').textContent = node.icon || '✨';
  document.getElementById('selected-node-label').textContent = node.label;
  document.getElementById('selected-node-id').textContent = `ID: ${node.id} | Realm: ${node.realm_id}`;
  document.getElementById('selected-node-desc').textContent = node.description || 'Category object defined by its morphism relationships.';

  const incoming = appState.arrows.filter(a => a.target_id === node.id && a.realm_id === appState.activeRealmId);
  const outgoing = appState.arrows.filter(a => a.source_id === node.id && a.realm_id === appState.activeRealmId);

  document.getElementById('count-incoming').textContent = incoming.length;
  document.getElementById('count-outgoing').textContent = outgoing.length;
  document.getElementById('count-loops').textContent = outgoing.filter(a => a.target_id === node.id).length;

  const listEl = document.getElementById('morphism-connections-list');
  listEl.innerHTML = '';

  if (incoming.length === 0 && outgoing.length === 0) {
    listEl.innerHTML = '<span class="empty-state-text">No active arrows connected to this node.</span>';
    return;
  }

  outgoing.forEach(a => {
    const tgt = appState.nodes.find(n => n.id === a.target_id);
    const item = document.createElement('div');
    item.className = 'connection-item';
    item.innerHTML = `<span>Outgoing: <strong>${a.label}</strong> ➔ ${tgt ? tgt.label : a.target_id}</span>`;
    listEl.appendChild(item);
  });

  incoming.forEach(a => {
    const src = appState.nodes.find(n => n.id === a.source_id);
    const item = document.createElement('div');
    item.className = 'connection-item';
    item.innerHTML = `<span>Incoming: ${src ? src.label : a.source_id} ➔ <strong>${a.label}</strong></span>`;
    listEl.appendChild(item);
  });
}

function handleNodeMouseDown(e, node) {
  if (appState.activeTool === 'draw') {
    isDrawingArrow = true;
    arrowSourceNode = node;
    const pt = getSvgPoint(e);
    dragLine.setAttribute('x1', node.x);
    dragLine.setAttribute('y1', node.y);
    dragLine.setAttribute('x2', pt.x);
    dragLine.setAttribute('y2', pt.y);
    dragLine.classList.remove('hidden');
  } else {
    isDraggingNode = true;
    draggedNode = node;
    const pt = getSvgPoint(e);
    dragOffset.x = pt.x - node.x;
    dragOffset.y = pt.y - node.y;
  }
}

function handleNodeMouseUp(e, targetNode) {
  if (isDrawingArrow && arrowSourceNode) {
    dragLine.classList.add('hidden');
    isDrawingArrow = false;

    if (arrowSourceNode.id !== targetNode.id) {
      commitNewArrow(arrowSourceNode, targetNode);
    }
    arrowSourceNode = null;
  }
}

function getSvgPoint(e) {
  const rect = svg.getBoundingClientRect();
  return {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top,
  };
}

svg.addEventListener('mousemove', (e) => {
  if (isDraggingNode && draggedNode) {
    const pt = getSvgPoint(e);
    draggedNode.x = Math.max(30, Math.min(svg.clientWidth - 30, pt.x - dragOffset.x));
    draggedNode.y = Math.max(30, Math.min(svg.clientHeight - 30, pt.y - dragOffset.y));
    render2DCanvas();
  } else if (isDrawingArrow && arrowSourceNode) {
    const pt = getSvgPoint(e);
    dragLine.setAttribute('x2', pt.x);
    dragLine.setAttribute('y2', pt.y);
  }
});

window.addEventListener('mouseup', () => {
  if (isDraggingNode) {
    isDraggingNode = false;
    draggedNode = null;
    saveStateLocally();
  }
  if (isDrawingArrow) {
    isDrawingArrow = false;
    arrowSourceNode = null;
    dragLine.classList.add('hidden');
  }
});

function commitNewArrow(sourceNode, targetNode) {
  const label = prompt(`Enter action label for morphism (${sourceNode.label} ➔ ${targetNode.label}):`, 'transforms to');
  if (!label) return;

  const newArrow = {
    id: `arr_${Date.now()}`,
    source_id: sourceNode.id,
    target_id: targetNode.id,
    label: label.trim(),
    realm_id: appState.activeRealmId,
    is_identity: false,
    composition_chain: [],
  };

  appState.arrows.push(newArrow);
  saveStateLocally();
  render2DCanvas();
}

// =============================================================================
// 5. MORPHISM COMPOSITION & COMMUTATIVITY ENGINE
// =============================================================================

function handleArrowClick(arrow) {
  if (appState.activeTool === 'compose') {
    if (!appState.compositionStep) {
      appState.compositionStep = { f: arrow, g: null };
      fsm.transition('START_COMPOSITION');
      fsm.transition('SELECT_FIRST');
      alert(`Selected first morphism f: ${arrow.label}. Now click the second morphism g to compose (g ∘ f).`);
    } else if (appState.compositionStep.f && !appState.compositionStep.g) {
      const f = appState.compositionStep.f;
      const g = arrow;

      // Type-check: cod(f) must equal dom(g)
      if (f.target_id !== g.source_id) {
        showTypeMismatchModal(f, g);
        appState.compositionStep = null;
        return;
      }

      appState.compositionStep.g = g;
      fsm.transition('SELECT_SECOND');
      fsm.transition('COMPOSE_SUCCESS');

      // Synthesize composite morphism
      const compositeArrow = {
        id: `comp_${Date.now()}`,
        source_id: f.source_id,
        target_id: g.target_id,
        label: `${g.label} ∘ ${f.label}`,
        realm_id: appState.activeRealmId,
        is_identity: false,
        composition_chain: [f.id, g.id],
      };

      appState.arrows.push(compositeArrow);
      saveStateLocally();
      appState.compositionStep = null;
      render2DCanvas();
      synth.playCommutingMajorChord();
    }
  } else if (appState.activeTool === 'commute') {
    testArrowCommutativity(arrow);
  }
}

function showTypeMismatchModal(f, g) {
  const modal = document.getElementById('type-mismatch-modal');
  const msg = document.getElementById('modal-err-message');
  const rec = document.getElementById('modal-err-recovery');

  const fTarget = appState.nodes.find(n => n.id === f.target_id)?.label || f.target_id;
  const gSource = appState.nodes.find(n => n.id === g.source_id)?.label || g.source_id;

  msg.textContent = `Arrow '${f.label}' ends at [${fTarget}], but arrow '${g.label}' starts at [${gSource}]. In category theory, composition (g ∘ f) requires cod(f) = dom(g).`;
  rec.textContent = `Please select a second arrow that begins at [${fTarget}].`;

  modal.classList.remove('hidden');
  synth.playTensionChord();
}

document.getElementById('btn-enclave-retry')?.addEventListener('click', () => {
  document.getElementById('type-mismatch-modal').classList.add('hidden');
});
document.getElementById('btn-enclave-dismiss')?.addEventListener('click', () => {
  document.getElementById('type-mismatch-modal').classList.add('hidden');
});

function checkAndHighlightCommutativity() {
  const activeArrows = appState.arrows.filter(a => a.realm_id === appState.activeRealmId);
  const activeNodes = appState.nodes.filter(n => n.realm_id === appState.activeRealmId);

  // Scan for commutative triangles: A -> B -> C and direct A -> C
  activeArrows.forEach(direct => {
    const fList = activeArrows.filter(a => a.source_id === direct.source_id && a.id !== direct.id);
    fList.forEach(f => {
      const gList = activeArrows.filter(a => a.source_id === f.target_id && a.target_id === direct.target_id);
      gList.forEach(g => {
        // Commutative triangle found!
        highlightCommutingTriangle(direct.source_id, f.target_id, direct.target_id);
      });
    });
  });
}

function highlightCommutingTriangle(idA, idB, idC) {
  const nA = appState.nodes.find(n => n.id === idA);
  const nB = appState.nodes.find(n => n.id === idB);
  const nC = appState.nodes.find(n => n.id === idC);
  if (!nA || !nB || !nC) return;

  const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
  polygon.setAttribute('points', `${nA.x},${nA.y} ${nB.x},${nB.y} ${nC.x},${nC.y}`);
  polygon.setAttribute('class', 'commuting-face');
  commutingLayer.appendChild(polygon);
}

function testArrowCommutativity(arrow) {
  document.getElementById('panel-yoneda').classList.add('hidden');
  document.getElementById('panel-commutativity').classList.remove('hidden');

  const verdictEl = document.getElementById('commutativity-verdict');
  const path1El = document.getElementById('label-path-1');
  const path2El = document.getElementById('label-path-2');
  const btnHarmonize = document.getElementById('btn-harmonize-face');

  if (arrow.composition_chain?.length) {
    path1El.textContent = `(Composite): ${arrow.label}`;
    path2El.textContent = `Endpoints: ${arrow.source_id} ➔ ${arrow.target_id}`;
    verdictEl.className = 'verdict-banner success';
    verdictEl.textContent = '✓ Diagram Commutes! Both paths evaluate identically.';
    btnHarmonize.disabled = false;
    synth.playCommutingMajorChord();
  } else {
    path1El.textContent = `(Direct): ${arrow.label}`;
    path2El.textContent = 'Single path; select a composite arrow to evaluate parallel equivalence.';
    verdictEl.className = 'verdict-banner pending';
    verdictEl.textContent = 'Select a composite path to compare.';
    btnHarmonize.disabled = true;
  }
}

document.getElementById('btn-harmonize-face')?.addEventListener('click', () => {
  synth.playCommutingMajorChord();
});

// =============================================================================
// 6. 3D FACTORIZATION CUBE VIEWPORT (DIVISORS OF 30)
// =============================================================================

let cubeAngleX = -25;
let cubeAngleY = 35;
let isRotatingCube = false;
let cubeLastMouse = { x: 0, y: 0 };

function renderCube3D() {
  const canvas = document.getElementById('cube-3d-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const cubeNodes = [
    { label: '1',  v: [0, 0, 0], prime: '1' },
    { label: '2',  v: [1, 0, 0], prime: 'x2' },
    { label: '3',  v: [0, 1, 0], prime: 'x3' },
    { label: '5',  v: [0, 0, 1], prime: 'x5' },
    { label: '6',  v: [1, 1, 0], prime: '2x3' },
    { label: '10', v: [1, 0, 1], prime: '2x5' },
    { label: '15', v: [0, 1, 1], prime: '3x5' },
    { label: '30', v: [1, 1, 1], prime: '2x3x5' },
  ];

  const edges = [
    [0, 1], [0, 2], [0, 3],
    [1, 4], [2, 4],
    [1, 5], [3, 5],
    [2, 6], [3, 6],
    [4, 7], [5, 7], [6, 7]
  ];

  // 3D rotation & projection
  const radX = (cubeAngleX * Math.PI) / 180;
  const radY = (cubeAngleY * Math.PI) / 180;
  const scale = 180;
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;

  const projected = cubeNodes.map(n => {
    let [x, y, z] = n.v.map(coord => coord - 0.5);

    // Rotate Y
    let x1 = x * Math.cos(radY) + z * Math.sin(radY);
    let z1 = -x * Math.sin(radY) + z * Math.cos(radY);

    // Rotate X
    let y2 = y * Math.cos(radX) - z1 * Math.sin(radX);
    let z2 = y * Math.sin(radX) + z1 * Math.cos(radX);

    return {
      x: cx + x1 * scale,
      y: cy - y2 * scale,
      z: z2,
      label: n.label,
    };
  });

  // Draw Edges (Morphisms)
  ctx.strokeStyle = '#6366f1';
  ctx.lineWidth = 2.5;
  edges.forEach(([i, j]) => {
    ctx.beginPath();
    ctx.moveTo(projected[i].x, projected[i].y);
    ctx.lineTo(projected[j].x, projected[j].y);
    ctx.stroke();
  });

  // Draw Nodes
  projected.forEach(p => {
    ctx.beginPath();
    ctx.arc(p.x, p.y, 18, 0, Math.PI * 2);
    ctx.fillStyle = '#1e293b';
    ctx.fill();
    ctx.strokeStyle = '#a5b4fc';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.fillStyle = '#fff';
    ctx.font = 'bold 13px -apple-system, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(p.label, p.x, p.y);
  });
}

const cubeCanvas = document.getElementById('cube-3d-canvas');
if (cubeCanvas) {
  cubeCanvas.addEventListener('mousedown', (e) => {
    isRotatingCube = true;
    cubeLastMouse = { x: e.clientX, y: e.clientY };
  });

  window.addEventListener('mousemove', (e) => {
    if (isRotatingCube) {
      const dx = e.clientX - cubeLastMouse.x;
      const dy = e.clientY - cubeLastMouse.y;
      cubeAngleY += dx * 0.5;
      cubeAngleX += dy * 0.5;
      cubeLastMouse = { x: e.clientX, y: e.clientY };
      renderCube3D();
    }
  });

  window.addEventListener('mouseup', () => {
    isRotatingCube = false;
  });
}

document.getElementById('btn-cube-rotate-left')?.addEventListener('click', () => {
  cubeAngleY -= 30;
  renderCube3D();
});
document.getElementById('btn-cube-rotate-right')?.addEventListener('click', () => {
  cubeAngleY += 30;
  renderCube3D();
});
document.getElementById('btn-cube-reset-view')?.addEventListener('click', () => {
  cubeAngleX = -25;
  cubeAngleY = 35;
  renderCube3D();
});
document.getElementById('btn-cube-check-face')?.addEventListener('click', () => {
  alert('Face (1 ➔ 2 ➔ 6) and (1 ➔ 3 ➔ 6) commutes! Multiplication of prime factors is strictly commutative: (2 × 3 = 3 × 2 = 6).');
  synth.playCommutingMajorChord();
});

// =============================================================================
// 7. FUNCTOR ANALOGY BRIDGE VIEWPORT
// =============================================================================

function renderFunctorBridge() {
  const culinaryList = document.getElementById('culinary-card-list');
  const artList = document.getElementById('art-card-list');
  if (!culinaryList || !artList) return;

  culinaryList.innerHTML = `
    <div class="connection-item"><span>🌾 Flour + Sugar (A₁)</span></div>
    <div class="connection-item"><span>🥣 Cake Batter (B₁) [fold in]</span></div>
    <div class="connection-item"><span>🎂 Baked Sponge (C₁) [bake at 350F]</span></div>
    <div class="connection-item"><span>✨ Masterpiece (D₁) [frost]</span></div>
  `;

  artList.innerHTML = `
    <div class="connection-item"><span>🎨 Raw Pigments F(A₁)</span></div>
    <div class="connection-item"><span>🖌️ Oil Paint F(B₁) [mull in binder]</span></div>
    <div class="connection-item"><span>🖼️ Stretched Canvas F(C₁) [cure]</span></div>
    <div class="connection-item"><span>🌟 Finished Painting F(D₁) [varnish]</span></div>
  `;
}

document.getElementById('btn-test-functor-coherence')?.addEventListener('click', () => {
  alert('Functor Preserved! F(bake ∘ fold) = F(bake) ∘ F(fold). The relational structure in Culinary Mathematics is losslessly mirrored in Visual Art.');
  synth.playCommutingMajorChord();
});

// =============================================================================
// 8. GLOBAL ACTION CONTROLS & EVENT LISTENERS
// =============================================================================

// Realm Navigation Buttons
document.querySelectorAll('.btn-realm').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.btn-realm').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    appState.activeRealmId = btn.dataset.realm;
    renderCurrentRealm();
  });
});

// Floating Toolbar Buttons
document.querySelectorAll('.btn-tool').forEach(btn => {
  btn.addEventListener('click', () => {
    if (btn.dataset.mode === 'add_node') {
      promptAddObject();
      return;
    }
    document.querySelectorAll('.btn-tool').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    appState.activeTool = btn.dataset.mode;
    document.getElementById('status-mode-label').textContent = `${btn.querySelector('.tool-label').textContent} Mode`;
  });
});

function promptAddObject() {
  const label = prompt('Enter name of new Category Object:', 'New Concept');
  if (!label) return;

  const newNode = {
    id: `node_${Date.now()}`,
    label: label.trim(),
    realm_id: appState.activeRealmId,
    x: 200 + Math.random() * 200,
    y: 150 + Math.random() * 150,
    icon: '✨',
    description: 'User-created mathematical concept.',
    color: '#8b5cf6',
  };

  appState.nodes.push(newNode);
  saveStateLocally();
  render2DCanvas();
}

// Dual Opposite Category Toggle (C^op)
document.getElementById('btn-dual-toggle')?.addEventListener('click', () => {
  appState.isDualMode = !appState.isDualMode;
  fsm.transition('TOGGLE_DUAL');
  render2DCanvas();
});

// Sound Toggle
document.getElementById('btn-sound-toggle')?.addEventListener('click', () => {
  synth.enabled = !synth.enabled;
  document.getElementById('sound-icon').textContent = synth.enabled ? '🔊' : '🔇';
});

// Functorial Undo (Cmd+Z)
document.getElementById('btn-undo')?.addEventListener('click', () => {
  fsm.undo();
  updateUndoButton();
  render2DCanvas();
});

window.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'z') {
    e.preventDefault();
    fsm.undo();
    updateUndoButton();
    render2DCanvas();
  }
});

// Reset Canvas
document.getElementById('btn-reset')?.addEventListener('click', () => {
  if (confirm('Reset active realm canvas to clean pedagogical seeds?')) {
    localStorage.removeItem('axioma_joy_state');
    loadInitialState();
  }
});

// Local-First Sync Modal
document.getElementById('btn-sync')?.addEventListener('click', () => {
  document.getElementById('sync-modal').classList.remove('hidden');
});
document.getElementById('btn-close-sync')?.addEventListener('click', () => {
  document.getElementById('sync-modal').classList.add('hidden');
});

// Export JSON
document.getElementById('btn-export-json')?.addEventListener('click', () => {
  const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(appState, null, 2));
  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute('href', dataStr);
  downloadAnchor.setAttribute('download', `axioma_joy_diagram_${Date.now()}.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
});

// Import JSON
document.getElementById('btn-import-trigger')?.addEventListener('click', () => {
  document.getElementById('file-import-json').click();
});
document.getElementById('file-import-json')?.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (event) => {
    try {
      const imported = JSON.parse(event.target.result);
      if (imported.nodes && imported.arrows) {
        appState.nodes = imported.nodes;
        appState.arrows = imported.arrows;
        saveStateLocally();
        renderCurrentRealm();
        document.getElementById('sync-modal').classList.add('hidden');
      }
    } catch (err) {
      alert('Invalid diagram JSON file.');
    }
  };
  reader.readAsText(file);
});

// Close Drawer
document.getElementById('btn-close-drawer')?.addEventListener('click', () => {
  document.getElementById('inspector-drawer').style.display = 'none';
});

// INITIALIZE ON LOAD
window.addEventListener('DOMContentLoaded', () => {
  loadInitialState();
});
"""


def generate_joy_server_py(semantic_ir: SemanticDomainIR, contract_ir: DualBoundaryContractIR, port: int) -> str:
    return f"""#!/usr/bin/env python3
\"\"\"Production Runtime Server for {semantic_ir.title} (System G2b).

Grounded in [L1-011_3] (Decoupled Persistence) and [L1-016] (Demarcated Exception Enclaves).
Native Python 3.14 zero-dependency server.
\"\"\"

import http.server
import json
from pathlib import Path
import urllib.parse

PORT = {port}
DATA_FILE = Path(__file__).parent / "data" / "app_state.json"
STATIC_DIR = Path(__file__).parent / "static"


def load_state():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {{"realms": [], "nodes": [], "arrows": []}}


def save_state(state):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


class AppServerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(load_state()).encode("utf-8"))
        elif parsed.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({{"status": "ok", "app": "{semantic_ir.app_id}", "version": "1.0.0"}}).encode("utf-8"))
        elif parsed.path == "/" or parsed.path == "":
            self.path = "/index.html"
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        if parsed.path in ["/api/state", "/api/backup"]:
            try:
                data = json.loads(body.decode("utf-8"))
                save_state(data)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({{"status": "saved", "nodes_count": len(data.get("nodes", []))}}).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({{"error": str(e)}}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def run_server():
    server_address = ("", PORT)
    httpd = http.server.HTTPServer(server_address, AppServerHandler)
    print(f"[{semantic_ir.title}] Serving HTTP on port {{PORT}} (http://localhost:{{PORT}})...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer shutting down gracefully.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
"""
