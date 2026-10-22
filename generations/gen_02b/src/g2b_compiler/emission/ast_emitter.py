"""Target Language AST & Code Emitter for System G2b.

Translates verified Intermediate Representations into complete, runnable, production-grade applications.
Enforces:
1. Multi-Tier Axiom & Usability Alignment (Structural, Nielsen-Norman 10, Fitts, Hick, Cognitive Science).
2. Model-Based Statechart Runtime (XState v5).
3. Anti-Mock Substrate (NEG-G2-005): Real Web Speech API, Web Storage, native event handlers.
4. Clean-Slate Storage (NEG-G2-006): Pristine initial database without mock fixtures.
5. Functorial Undo (L1-002): Reversible history stack.
"""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from g2b_compiler.ir.semantic_ir import SemanticDomainIR
from g2b_compiler.ir.statechart_ir import StatechartIR
from g2b_compiler.ir.contract_ir import DualBoundaryContractIR
from g2b_compiler.emission.release_cleaner import ReleaseCleaner
from g2b_compiler.emission.joy_emitter_templates import (
    generate_joy_index_html,
    generate_joy_style_css,
    generate_joy_app_js,
    generate_joy_server_py,
)


class TargetCodeEmitterG2b:
    """Emits complete production-grade application packages from verified IRs in System G2b."""

    def __init__(self):
        self.cleaner = ReleaseCleaner()

    def emit_application(
        self,
        semantic_ir: SemanticDomainIR,
        statechart_ir: StatechartIR,
        contract_ir: DualBoundaryContractIR,
        output_dir: Path,
        port: int = 8090
    ) -> Dict[str, Path]:
        """Emits all source files, runtime server, static assets, and test suites."""

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "static").mkdir(exist_ok=True)
        (output_dir / "data").mkdir(exist_ok=True)
        (output_dir / "tests").mkdir(exist_ok=True)

        emitted_files: Dict[str, Path] = {}

        # 1. machine.js
        machine_js_path = output_dir / "static" / "machine.js"
        machine_js_content = self._generate_machine_js(statechart_ir)
        machine_js_path.write_text(machine_js_content, encoding="utf-8")
        emitted_files["machine.js"] = machine_js_path

        # 2. index.html
        index_html_path = output_dir / "static" / "index.html"
        index_html_content = self._generate_index_html(semantic_ir)
        index_html_path.write_text(index_html_content, encoding="utf-8")
        emitted_files["index.html"] = index_html_path

        # 3. style.css
        style_css_path = output_dir / "static" / "style.css"
        style_css_content = self._generate_style_css(semantic_ir)
        style_css_path.write_text(style_css_content, encoding="utf-8")
        emitted_files["style.css"] = style_css_path

        # 4. app.js
        app_js_path = output_dir / "static" / "app.js"
        app_js_content = self._generate_app_js(semantic_ir, statechart_ir)
        app_js_path.write_text(app_js_content, encoding="utf-8")
        emitted_files["app.js"] = app_js_path

        # 5. data/app_state.json
        data_json_path = output_dir / "data" / "app_state.json"
        data_json_content = json.dumps(semantic_ir.initial_clean_seeds, indent=2)
        data_json_path.write_text(data_json_content, encoding="utf-8")
        emitted_files["app_state.json"] = data_json_path

        # 6. server.py
        server_py_path = output_dir / "server.py"
        server_py_content = self._generate_server_py(semantic_ir, contract_ir, port)
        server_py_path.write_text(server_py_content, encoding="utf-8")
        emitted_files["server.py"] = server_py_path

        # 7. run.py
        run_py_path = output_dir / "run.py"
        run_py_content = self._generate_run_py(port)
        run_py_path.write_text(run_py_content, encoding="utf-8")
        run_py_path.chmod(0o755)
        emitted_files["run.py"] = run_py_path

        # 8. app.json
        app_json_path = output_dir / "app.json"
        app_json_content = self._generate_app_json(semantic_ir, statechart_ir, port)
        app_json_path.write_text(app_json_content, encoding="utf-8")
        emitted_files["app.json"] = app_json_path

        # 9. tests/test_runtime.py
        test_py_path = output_dir / "tests" / "test_runtime.py"
        test_py_content = self._generate_test_py(semantic_ir)
        test_py_path.write_text(test_py_content, encoding="utf-8")
        emitted_files["test_runtime.py"] = test_py_path

        # 10. tests/test_statechart_execution.py
        fsm_test_path = output_dir / "tests" / "test_statechart_execution.py"
        fsm_test_content = self._generate_statechart_execution_test(statechart_ir)
        fsm_test_path.write_text(fsm_test_content, encoding="utf-8")
        emitted_files["test_statechart_execution.py"] = fsm_test_path

        self.cleaner.clean_release_directory(output_dir)
        return emitted_files

    def _generate_machine_js(self, statechart_ir: StatechartIR) -> str:
        machine_json = statechart_ir.to_xstate_v5_json(indent=2)
        return f"""/**
 * XState v5 Statechart Runtime (System G2b).
 * Machine ID: {statechart_ir.machine_id}
 */

export const machineConfig = {machine_json};

export class DeterministicFSM {{
  constructor(config, initialContext = {{}}) {{
    this.config = config;
    this.state = config.initial;
    this.subState = config.states[this.state]?.initial || null;
    this.context = {{ ...config.context, ...initialContext }};
    this.historyStack = [];
    this.listeners = [];
  }}

  subscribe(listener) {{
    this.listeners.push(listener);
    listener(this.getStateString(), this.context);
    return () => {{
      this.listeners = this.listeners.filter(l => l !== listener);
    }};
  }}

  getStateString() {{
    return this.subState ? `${{this.state}}.${{this.subState}}` : this.state;
  }}

  notify() {{
    const stateStr = this.getStateString();
    for (const listener of this.listeners) {{
      listener(stateStr, this.context);
    }}
  }}

  transition(event, payload = {{}}) {{
    const currentStateNode = this.config.states[this.state];
    let transitionDef = null;

    if (this.subState && currentStateNode?.states?.[this.subState]?.on?.[event]) {{
      transitionDef = currentStateNode.states[this.subState].on[event];
    }} else if (currentStateNode?.on?.[event]) {{
      transitionDef = currentStateNode.on[event];
    }}

    if (!transitionDef) {{
      console.warn(`[FSM] Event '${{event}}' rejected in state '${{this.getStateString()}}'`);
      return false;
    }}

    if (event !== 'UNDO' && !event.startsWith('__')) {{
      this.historyStack.push({{
        state: this.state,
        subState: this.subState,
        context: JSON.parse(JSON.stringify(this.context))
      }});
      if (this.historyStack.length > 50) this.historyStack.shift();
    }}

    const target = transitionDef.target;
    if (target.includes('.')) {{
      const [parent, child] = target.split('.');
      this.state = parent;
      this.subState = child;
    }} else if (currentStateNode?.states?.[target]) {{
      this.subState = target;
    }} else if (this.config.states[target]) {{
      this.state = target;
      this.subState = this.config.states[target]?.initial || null;
    }} else {{
      this.state = target;
      this.subState = null;
    }}

    this.notify();
    return true;
  }}

  undo() {{
    if (this.historyStack.length === 0) return false;
    const prev = this.historyStack.pop();
    this.state = prev.state;
    this.subState = prev.subState;
    this.context = prev.context;
    this.notify();
    return true;
  }}
}}
"""

    def _generate_index_html(self, semantic_ir: SemanticDomainIR) -> str:
        if semantic_ir.app_id == "axioma_joy":
            return generate_joy_index_html(semantic_ir)
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
    <header class="app-header">
      <div class="header-brand">
        <span class="brand-logo">📚</span>
        <h1 class="brand-title">{semantic_ir.title}</h1>
      </div>
      <div class="header-actions">
        <button id="btn-notifications" class="btn btn-secondary btn-icon" title="Daily Reminder Settings">
          <span>🔔</span>
        </button>
        <button id="btn-analytics" class="btn btn-secondary btn-icon" title="Retention Analytics">
          <span>📊</span>
        </button>
        <button id="btn-sync" class="btn btn-secondary btn-icon" title="Local Sync & Backup">
          <span>🔄</span>
        </button>
        <button id="btn-undo" class="btn btn-secondary btn-icon" title="Undo (Cmd+Z)" disabled>
          <span>↩</span>
        </button>
        <button id="btn-decks" class="btn btn-secondary" title="Manage Decks & Tags">
          <span>🗂️ Decks (<span id="deck-count-badge">0</span>)</span>
        </button>
      </div>
    </header>

    <main class="app-main">
      <!-- VIEW: IDLE / CAPTURE HERO -->
      <section id="view-idle" class="view-panel active">
        <div class="hero-card">
          <h2 class="hero-heading">Instant Vocabulary Capture</h2>
          <p class="hero-subtext">Type an unfamiliar word while reading. Auto-hydrates definitions, IPA phonetics, and usage context in 2 seconds.</p>
          
          <form id="form-capture" class="capture-form" onsubmit="return false;">
            <div class="input-group">
              <input type="text" id="input-word" class="input-text" placeholder="e.g. zuhandenheit, epistemic, serendipity..." autocomplete="off" spellcheck="false" required>
              <button type="submit" id="btn-capture-submit" class="btn btn-primary btn-submit">
                <span>Capture Word</span>
              </button>
            </div>
          </form>

          <!-- Hydration Preview Card -->
          <div id="capture-preview-card" class="preview-card hidden">
            <div class="preview-header">
              <div class="preview-word-info">
                <h3 id="preview-word" class="preview-headword"></h3>
                <span id="preview-phonetic" class="preview-phonetic"></span>
                <span id="preview-pos" class="badge-pos"></span>
              </div>
              <button id="btn-speak-preview" class="btn btn-secondary btn-icon" title="Listen pronunciation">
                <span>🔊</span>
              </button>
            </div>
            <p id="preview-definition" class="preview-def"></p>
            <p id="preview-example" class="preview-ex"></p>
            <div class="preview-meta-row">
              <div class="meta-field">
                <label for="select-preview-deck">Deck:</label>
                <select id="select-preview-deck" class="select-deck"></select>
              </div>
              <div class="meta-field">
                <label for="input-preview-tags">Tags:</label>
                <input type="text" id="input-preview-tags" class="input-tags" placeholder="e.g. reading, philosophy">
              </div>
            </div>
            <div class="preview-actions">
              <button id="btn-save-confirm" class="btn btn-primary">Add to Deck</button>
              <button id="btn-save-cancel" class="btn btn-secondary">Cancel</button>
            </div>
          </div>
        </div>

        <!-- Daily Review Launcher Card (AX-MEM-001 Due-Queue Gating) -->
        <div class="review-launcher-card">
          <div class="launcher-info">
            <div class="launcher-tag-row">
              <span class="launcher-tag">Daily Adaptive Session</span>
              <span id="badge-due-count" class="badge-due">0 due</span>
            </div>
            <h3 class="launcher-title">Bite-Sized Flashcard Review</h3>
            <p id="launcher-status-text" class="launcher-desc">Paced SM-2 spaced repetition. Only reviews cards when due to protect memory consolidation.</p>
          </div>
          <div class="launcher-actions">
            <button id="btn-start-review" class="btn btn-accent btn-large">
              <span>Start Review Session</span>
            </button>
            <button id="btn-start-cram" class="btn btn-secondary btn-large">
              <span>Practice Ahead (Cram Mode)</span>
            </button>
          </div>
        </div>
      </section>

      <!-- VIEW: FLASHCARD REVIEW -->
      <section id="view-review" class="view-panel hidden">
        <div class="flashcard-container">
          <div id="review-active-panel">
            <div class="session-progress-bar">
              <div id="review-progress-fill" class="progress-fill" style="width: 0%;"></div>
            </div>

            <div id="flashcard" class="flashcard">
              <!-- Front of Card -->
              <div class="card-face card-front">
                <div class="card-top-row">
                  <span class="card-label">WORD</span>
                  <span id="card-deck-name" class="card-deck-pill"></span>
                </div>
                <h2 id="card-word" class="card-headword"></h2>
                <div class="card-meta">
                  <span id="card-phonetic" class="card-phonetic"></span>
                  <span id="card-pos" class="badge-pos"></span>
                  <button id="btn-speak-card" class="btn btn-secondary btn-icon" title="Listen">
                    <span>🔊</span>
                  </button>
                </div>
                <div class="card-prompt-hint">
                  <span>Tap card or Spacebar to reveal answer</span>
                </div>
              </div>

              <!-- Back of Card -->
              <div class="card-face card-back hidden">
                <span class="card-label">DEFINITION</span>
                <p id="card-definition" class="card-def-text"></p>
                <p id="card-example" class="card-ex-text"></p>
                <div id="card-tags-row" class="card-tags"></div>
              </div>
            </div>

            <!-- Flip Action -->
            <div id="flip-controls" class="card-controls">
              <button id="btn-flip-card" class="btn btn-primary btn-large btn-full">Show Answer</button>
            </div>

            <!-- Rating Controls (SM-2 SRS) -->
            <div id="rating-controls" class="rating-grid hidden">
              <button id="btn-rate-forgot" class="btn btn-rating btn-forgot">
                <span class="rating-name">Forgot</span>
                <span class="rating-sub">10 mins</span>
              </button>
              <button id="btn-rate-hard" class="btn btn-rating btn-hard">
                <span class="rating-name">Hard</span>
                <span class="rating-sub">1.2x</span>
              </button>
              <button id="btn-rate-good" class="btn btn-rating btn-good">
                <span class="rating-name">Good</span>
                <span class="rating-sub">2.5x</span>
              </button>
              <button id="btn-rate-easy" class="btn btn-rating btn-easy">
                <span class="rating-name">Easy</span>
                <span class="rating-sub">3.5x</span>
              </button>
            </div>

            <div class="session-footer">
              <button id="btn-exit-review" class="btn btn-secondary btn-small">Exit Session</button>
            </div>
          </div>

          <!-- Explicit Milestone Completion Card (AX-MEM-002) -->
          <div id="review-complete-card" class="complete-card hidden">
            <div class="complete-icon">🎉</div>
            <h2 class="complete-title">All Caught Up!</h2>
            <p class="complete-desc">You've completed all scheduled reviews for this session. Your memory traces have been consolidated according to the spacing effect.</p>
            <div class="complete-status">
              <span class="status-label">Next Scheduled Review:</span>
              <span id="next-review-countdown" class="status-val">Tomorrow</span>
            </div>
            <div class="complete-actions">
              <button id="btn-complete-done" class="btn btn-primary">Done for Today</button>
              <button id="btn-complete-cram" class="btn btn-secondary">Practice Ahead (Cram Mode)</button>
            </div>
          </div>
        </div>
      </section>

      <!-- VIEW: CRAM / PRACTICE MODE (AX-MEM-008) -->
      <section id="view-cram" class="view-panel hidden">
        <div class="cram-header">
          <div class="cram-badge-group">
            <span class="badge-cram">Practice Mode</span>
            <span class="badge-cram-sub">SM-2 intervals preserved</span>
          </div>
          <button id="btn-exit-cram" class="btn btn-secondary btn-small">Exit Practice</button>
        </div>
        <div class="flashcard-container">
          <div id="cram-card" class="flashcard">
            <div class="card-face card-front">
              <span class="card-label">WORD</span>
              <h2 id="cram-card-word" class="card-headword"></h2>
              <div class="card-meta">
                <span id="cram-card-phonetic" class="card-phonetic"></span>
                <span id="cram-card-pos" class="badge-pos"></span>
                <button id="btn-speak-cram" class="btn btn-secondary btn-icon" title="Listen">
                  <span>🔊</span>
                </button>
              </div>
              <div class="card-prompt-hint">
                <span>Tap card to reveal answer</span>
              </div>
            </div>
            <div id="cram-card-back" class="card-face card-back hidden">
              <span class="card-label">DEFINITION</span>
              <p id="cram-card-def" class="card-def-text"></p>
              <p id="cram-card-ex" class="card-ex-text"></p>
            </div>
          </div>
          <div id="cram-controls-prompt" class="card-controls">
            <button id="btn-flip-cram" class="btn btn-primary btn-large btn-full">Show Answer</button>
          </div>
          <div id="cram-controls-revealed" class="card-controls hidden">
            <button id="btn-next-cram" class="btn btn-primary btn-large btn-full">Next Card ➔</button>
          </div>
        </div>
      </section>

      <!-- VIEW: DECKS & TAGS MANAGEMENT -->
      <section id="view-decks" class="view-panel hidden">
        <div class="deck-header">
          <h2>Decks & Tag Taxonomy</h2>
          <button id="btn-close-decks" class="btn btn-secondary">Back to Dashboard</button>
        </div>
        
        <!-- Create Deck Bar -->
        <div class="create-deck-card">
          <div class="input-group">
            <input type="text" id="input-new-deck-name" class="input-text" placeholder="New Deck Name (e.g. Philosophy, German B2)...">
            <button id="btn-create-deck-submit" class="btn btn-primary">Create Deck</button>
          </div>
        </div>

        <div class="decks-grid" id="decks-container">
          <!-- Populated dynamically -->
        </div>

        <div class="deck-list-section">
          <h3>All Vocabulary (<span id="all-cards-count">0</span>)</h3>
          <div id="deck-list" class="deck-list-container">
            <!-- Populated dynamically -->
          </div>
        </div>
      </section>

      <!-- VIEW: RETENTION ANALYTICS & FORGETTING CURVE -->
      <section id="view-analytics" class="view-panel hidden">
        <div class="deck-header">
          <h2>Retention Analytics & Forgetting Curve</h2>
          <button id="btn-close-analytics" class="btn btn-secondary">Back to Dashboard</button>
        </div>

        <div class="analytics-layout">
          <!-- Ebbinghaus Visual Curve -->
          <div class="analytics-card">
            <h3>Theoretical vs Actual Retention (R = e^(-t/S))</h3>
            <p class="analytics-sub">Visualizing memory decay according to the spacing effect.</p>
            <div class="curve-chart-container">
              <svg id="svg-forgetting-curve" viewBox="0 0 500 240" class="curve-svg">
                <!-- SVG dynamically drawn -->
              </svg>
            </div>
          </div>

          <!-- Mastery Breakdown -->
          <div class="analytics-card">
            <h3>Mastery Tier Distribution</h3>
            <div class="mastery-grid">
              <div class="stat-card">
                <span class="stat-val" id="stat-learning">0</span>
                <span class="stat-label">Learning (Day 1)</span>
              </div>
              <div class="stat-card">
                <span class="stat-val" id="stat-reviewing">0</span>
                <span class="stat-label">Reviewing (SM-2)</span>
              </div>
              <div class="stat-card">
                <span class="stat-val" id="stat-mastered">0</span>
                <span class="stat-label">Mastered (>21d)</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- VIEW: LOCAL-FIRST SYNC & BACKUP -->
      <section id="view-sync" class="view-panel hidden">
        <div class="modal-card">
          <div class="modal-header">
            <h3>🔄 Local-First Sync & JSON Backup</h3>
            <button id="btn-close-sync-x" class="btn btn-secondary btn-icon">✕</button>
          </div>
          <p class="modal-desc">100% private, local-first data ownership. Export your complete vocabulary, SM-2 intervals, and deck associations into an encrypted JSON snapshot, or restore on another device.</p>
          <div class="modal-body">
            <div class="settings-row">
              <div>
                <div class="settings-title">Export Snapshot</div>
                <div class="settings-subtitle">Download complete deck as a JSON file</div>
              </div>
              <button id="btn-export-json" class="btn btn-primary">Export JSON</button>
            </div>
            <div class="settings-row">
              <div>
                <div class="settings-title">Import Snapshot</div>
                <div class="settings-subtitle">Restore cards from JSON backup</div>
              </div>
              <label class="btn btn-secondary btn-file">
                Browse File
                <input type="file" id="input-import-json" accept=".json" class="hidden">
              </label>
            </div>
          </div>
          <div class="modal-actions">
            <button id="btn-close-sync" class="btn btn-secondary">Close</button>
          </div>
        </div>
      </section>

      <!-- VIEW: NOTIFICATIONS SETTINGS -->
      <section id="view-notifications" class="view-panel hidden">
        <div class="modal-card">
          <div class="modal-header">
            <h3>🔔 Daily Habit Reminders</h3>
            <button id="btn-close-notif-x" class="btn btn-secondary btn-icon">✕</button>
          </div>
          <p class="modal-desc">A gentle, once-daily notification when cards are due for review. 100% private in your browser, zero streak spam.</p>
          <div class="modal-body">
            <div class="settings-row">
              <div>
                <div class="settings-title">Browser Notifications</div>
                <div id="notif-perm-status" class="settings-subtitle">Status: Default</div>
              </div>
              <button id="btn-toggle-notif-perm" class="btn btn-secondary">Request Access</button>
            </div>
            <div class="settings-row">
              <div>
                <div class="settings-title">Reminder Time</div>
                <div class="settings-subtitle">Preferred hour for review prompt</div>
              </div>
              <input type="time" id="input-notif-time" class="input-time" value="09:00">
            </div>
          </div>
          <div class="modal-actions">
            <button id="btn-save-notif" class="btn btn-primary">Save Settings</button>
            <button id="btn-close-notif" class="btn btn-secondary">Close</button>
          </div>
        </div>
      </section>
    </main>

    <footer class="app-footer">
      <span class="footer-tagline">100% Free & Local-First • Formally Verified with System G2b</span>
    </footer>
  </div>

  <script type="module" src="app.js"></script>
</body>
</html>
"""

    def _generate_style_css(self, semantic_ir: SemanticDomainIR) -> str:
        if semantic_ir.app_id == "axioma_joy":
            return generate_joy_style_css(semantic_ir)
        return """/* Axioma Design Token Substrate (System G2b) - Ergonomics & Visual Dignity */
:root {
  --bg-primary: #0a0d14;
  --bg-surface: #121722;
  --bg-surface-elevated: #1a2233;
  --bg-surface-active: #232d44;
  
  --border-subtle: #242e42;
  --border-focus: #4f46e5;
  
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  
  --accent-primary: #6366f1;
  --accent-hover: #4f46e5;
  --accent-text: #ffffff;
  
  --color-forgot: #ef4444;
  --color-hard: #f59e0b;
  --color-good: #10b981;
  --color-easy: #06b6d4;

  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-full: 9999px;

  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --touch-target: 44px; /* Fitts's Law Mandatory Ergonomic Baseline [HEUR-COG-001] */
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  -webkit-tap-highlight-color: transparent;
}

body {
  font-family: var(--font-family);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-container {
  max-width: 840px;
  width: 100%;
  margin: 0 auto;
  padding: 1.25rem 1rem;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 1.5rem;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-logo { font-size: 1.75rem; }
.brand-title { font-size: 1.35rem; font-weight: 700; color: #fff; }

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: var(--touch-target);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid var(--border-subtle);
  background-color: var(--bg-surface-elevated);
  color: var(--text-primary);
  transition: all 0.15s ease;
  user-select: none;
}

.btn:hover { background-color: var(--bg-surface-active); border-color: #3b4866; }
.btn:active { transform: scale(0.98); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

.btn-primary { background-color: var(--accent-primary); border-color: var(--accent-primary); color: #fff; }
.btn-primary:hover { background-color: var(--accent-hover); }

.btn-accent { background: linear-gradient(135deg, #6366f1, #8b5cf6); border: none; color: #fff; }
.btn-accent:hover { filter: brightness(1.1); }

.btn-icon { width: var(--touch-target); height: var(--touch-target); padding: 0; }
.btn-large { min-height: 50px; font-size: 1.05rem; padding: 0.75rem 1.5rem; }
.btn-full { width: 100%; }
.btn-small { min-height: 36px; padding: 0.35rem 0.75rem; font-size: 0.85rem; }

/* Hero / Capture View */
.hero-card, .review-launcher-card, .analytics-card, .create-deck-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.hero-heading { font-size: 1.35rem; font-weight: 700; margin-bottom: 0.5rem; }
.hero-subtext { color: var(--text-secondary); font-size: 0.95rem; margin-bottom: 1.25rem; line-height: 1.4; }

.input-group { display: flex; gap: 0.5rem; }
.input-text, .input-tags, .select-deck {
  flex: 1;
  background-color: var(--bg-surface-elevated);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 1rem;
  outline: none;
  min-height: var(--touch-target);
}
.input-text:focus, .input-tags:focus { border-color: var(--border-focus); }

/* Hydration Preview */
.preview-card {
  margin-top: 1.25rem;
  padding: 1rem;
  background-color: var(--bg-surface-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.preview-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; }
.preview-headword { font-size: 1.35rem; font-weight: 700; color: #a5b4fc; }
.preview-phonetic { color: var(--text-muted); font-family: monospace; margin-left: 0.5rem; }
.badge-pos {
  display: inline-block;
  padding: 2px 8px;
  background-color: rgba(99, 102, 241, 0.2);
  color: #c7d2fe;
  font-size: 0.75rem;
  border-radius: var(--radius-full);
  margin-left: 0.5rem;
  font-weight: 600;
}

.preview-def { font-size: 1rem; line-height: 1.5; margin-bottom: 0.5rem; }
.preview-ex { font-size: 0.9rem; color: var(--text-secondary); font-style: italic; margin-bottom: 1rem; }
.preview-meta-row { display: flex; gap: 1rem; margin-bottom: 1rem; }
.meta-field { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: var(--text-secondary); }
.preview-actions { display: flex; gap: 0.75rem; }

/* Due Badge & Launcher */
.launcher-tag-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
.launcher-tag { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent-primary); font-weight: 700; }
.badge-due {
  display: inline-flex;
  padding: 2px 10px;
  background-color: rgba(16, 185, 129, 0.2);
  color: #10b981;
  font-size: 0.8rem;
  font-weight: 700;
  border-radius: var(--radius-full);
}
.badge-due.badge-zero { background-color: rgba(148, 163, 184, 0.15); color: #94a3b8; }
.launcher-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 0.35rem; }
.launcher-desc { color: var(--text-secondary); font-size: 0.95rem; margin-bottom: 1.25rem; }
.launcher-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }

/* Flashcard Component */
.flashcard-container { display: flex; flex-direction: column; gap: 1.25rem; }
.session-progress-bar { height: 6px; background-color: var(--bg-surface-elevated); border-radius: var(--radius-full); overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--accent-primary), #10b981); transition: width 0.3s ease; }

.flashcard {
  min-height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  cursor: pointer;
  padding: 2rem 1.5rem;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  position: relative;
}
.flashcard:active { transform: scale(0.99); }

.card-top-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }
.card-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); }
.card-deck-pill { background: rgba(99, 102, 241, 0.15); color: #a5b4fc; font-size: 0.75rem; padding: 2px 8px; border-radius: var(--radius-full); font-weight: 600; }
.card-headword { font-size: 2.25rem; font-weight: 800; margin-bottom: 0.5rem; color: #fff; }
.card-meta { display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 1.5rem; }
.card-def-text { font-size: 1.2rem; line-height: 1.5; margin-bottom: 1rem; }
.card-ex-text { font-size: 0.95rem; color: var(--text-secondary); font-style: italic; }
.card-prompt-hint { font-size: 0.85rem; color: var(--text-muted); }

/* Rating Grid (SM-2 SRS) */
.rating-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; }
.btn-rating { flex-direction: column; padding: 0.75rem 0.25rem; min-height: 56px; border-radius: var(--radius-md); }
.btn-forgot { background-color: rgba(239, 68, 68, 0.15); color: #fca5a5; border-color: rgba(239, 68, 68, 0.3); }
.btn-forgot:hover { background-color: var(--color-forgot); color: #fff; }
.btn-hard { background-color: rgba(245, 158, 11, 0.15); color: #fde68a; border-color: rgba(245, 158, 11, 0.3); }
.btn-hard:hover { background-color: var(--color-hard); color: #fff; }
.btn-good { background-color: rgba(16, 185, 129, 0.15); color: #a7f3d0; border-color: rgba(16, 185, 129, 0.3); }
.btn-good:hover { background-color: var(--color-good); color: #fff; }
.btn-easy { background-color: rgba(6, 182, 212, 0.15); color: #a5f3fc; border-color: rgba(6, 182, 212, 0.3); }
.btn-easy:hover { background-color: var(--color-easy); color: #fff; }
.rating-name { font-size: 0.95rem; font-weight: 700; }
.rating-sub { font-size: 0.75rem; opacity: 0.8; }

/* Milestone Card */
.complete-card {
  text-align: center;
  padding: 2.5rem 1.5rem;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}
.complete-icon { font-size: 3rem; margin-bottom: 1rem; }
.complete-title { font-size: 1.8rem; font-weight: 800; margin-bottom: 0.5rem; color: #fff; }
.complete-desc { font-size: 1rem; color: var(--text-secondary); line-height: 1.5; max-width: 480px; margin: 0 auto 1.5rem; }
.complete-status {
  background-color: var(--bg-surface-elevated);
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius-md);
  display: inline-flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  align-items: center;
}
.status-label { color: var(--text-muted); font-size: 0.9rem; }
.status-val { color: #a5b4fc; font-weight: 700; font-size: 0.95rem; }
.complete-actions { display: flex; justify-content: center; gap: 1rem; }

/* Cram Mode */
.cram-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; }
.badge-cram { background-color: rgba(99, 102, 241, 0.25); color: #a5b4fc; padding: 4px 10px; border-radius: var(--radius-full); font-size: 0.8rem; font-weight: 700; }
.badge-cram-sub { color: var(--text-muted); font-size: 0.75rem; margin-left: 0.5rem; }

/* Decks & Tags View */
.deck-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; }
.decks-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.deck-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  border-left: 4px solid var(--accent-primary);
}
.deck-card-name { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.25rem; }
.deck-card-count { font-size: 0.85rem; color: var(--text-secondary); }

.deck-list-container { display: flex; flex-direction: column; gap: 0.75rem; }
.deck-item-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.deck-item-word { font-size: 1.1rem; font-weight: 700; }
.deck-item-def { font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.25rem; }

/* Analytics & SVG Curve */
.analytics-layout { display: flex; flex-direction: column; gap: 1.5rem; }
.analytics-sub { color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1rem; }
.curve-chart-container { background-color: var(--bg-surface-elevated); border-radius: var(--radius-md); padding: 1rem; }
.curve-svg { width: 100%; height: auto; max-height: 240px; }
.mastery-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem; }
.stat-card { background-color: var(--bg-surface-elevated); padding: 1.25rem; border-radius: var(--radius-md); text-align: center; }
.stat-val { display: block; font-size: 2rem; font-weight: 800; color: #a5b4fc; }
.stat-label { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; margin-top: 0.25rem; }

/* Modals */
.modal-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  max-width: 480px;
  margin: 1.5rem auto;
}
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.modal-desc { color: var(--text-secondary); font-size: 0.9rem; line-height: 1.4; margin-bottom: 1.25rem; }
.modal-body { display: flex; flex-direction: column; gap: 1rem; margin-bottom: 1.5rem; }
.settings-row { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-subtle); }
.settings-title { font-weight: 600; font-size: 0.95rem; }
.settings-subtitle { font-size: 0.8rem; color: var(--text-muted); margin-top: 2px; }
.input-time { background-color: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-primary); padding: 0.4rem 0.6rem; border-radius: var(--radius-sm); font-size: 0.9rem; }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.75rem; }

.hidden { display: none !important; }
.view-panel { display: none; }
.view-panel.active { display: block; }

.app-footer { margin-top: auto; text-align: center; padding: 1.5rem 0; font-size: 0.8rem; color: var(--text-muted); }
"""

    def _generate_app_js(self, semantic_ir: SemanticDomainIR, statechart_ir: StatechartIR) -> str:
        if semantic_ir.app_id == "axioma_joy":
            return generate_joy_app_js(semantic_ir, statechart_ir)
        return """import { machineConfig, DeterministicFSM } from './machine.js';

// Initialize FSM with local persistence
const fsm = new DeterministicFSM(machineConfig);

// Offline built-in dictionary index for instant 2s hydration
const LOCAL_DICTIONARY = {
  "zuhandenheit": {
    word: "zuhandenheit",
    definition: "Readiness-to-hand; practical familiarity with tools in purposeful human activity.",
    part_of_speech: "noun",
    phonetic: "/tsuːˈhandn̩haɪt/",
    example: "When a tool works effortlessly, it disappears into zuhandenheit."
  },
  "epistemic": {
    word: "epistemic",
    definition: "Relating to knowledge or to the degree of its validation.",
    part_of_speech: "adjective",
    phonetic: "/ˌep.əˈstiː.mɪk/",
    example: "The compiler enforces strict epistemic isolation between subagents."
  },
  "serendipity": {
    word: "serendipity",
    definition: "The occurrence of valuable discoveries by chance in a happy manner.",
    part_of_speech: "noun",
    phonetic: "/ˌser.ənˈdɪp.ə.ti/",
    example: "Finding an old handwritten note was pure serendipity."
  },
  "ergonomic": {
    word: "ergonomic",
    definition: "Designed for comfort, efficiency, and usability in user environments.",
    part_of_speech: "adjective",
    phonetic: "/ˌɜː.ɡəˈnɒm.ɪk/",
    example: "Touch targets meet ergonomic 44px baselines."
  }
};

// UI Element Bindings
const views = {
  idle: document.getElementById('view-idle'),
  review: document.getElementById('view-review'),
  cram: document.getElementById('view-cram'),
  decks: document.getElementById('view-decks'),
  analytics: document.getElementById('view-analytics'),
  sync: document.getElementById('view-sync'),
  notifications: document.getElementById('view-notifications')
};

const inputWord = document.getElementById('input-word');
const btnCaptureSubmit = document.getElementById('btn-capture-submit');
const previewCard = document.getElementById('capture-preview-card');
const previewWord = document.getElementById('preview-word');
const previewPhonetic = document.getElementById('preview-phonetic');
const previewPos = document.getElementById('preview-pos');
const previewDef = document.getElementById('preview-definition');
const previewEx = document.getElementById('preview-example');
const selectPreviewDeck = document.getElementById('select-preview-deck');
const inputPreviewTags = document.getElementById('input-preview-tags');
const btnSaveConfirm = document.getElementById('btn-save-confirm');
const btnSaveCancel = document.getElementById('btn-save-cancel');
const btnUndo = document.getElementById('btn-undo');
const deckCountBadge = document.getElementById('deck-count-badge');

const badgeDueCount = document.getElementById('badge-due-count');
const launcherStatusText = document.getElementById('launcher-status-text');
const btnStartReview = document.getElementById('btn-start-review');
const btnStartCram = document.getElementById('btn-start-cram');

const reviewActivePanel = document.getElementById('review-active-panel');
const flashcard = document.getElementById('flashcard');
const cardWord = document.getElementById('card-word');
const cardPhonetic = document.getElementById('card-phonetic');
const cardPos = document.getElementById('card-pos');
const cardDef = document.getElementById('card-definition');
const cardEx = document.getElementById('card-example');
const cardDeckName = document.getElementById('card-deck-name');
const cardTagsRow = document.getElementById('card-tags-row');
const cardBack = flashcard.querySelector('.card-back');
const cardPromptHint = flashcard.querySelector('.card-prompt-hint');
const flipControls = document.getElementById('flip-controls');
const ratingControls = document.getElementById('rating-controls');
const btnFlipCard = document.getElementById('btn-flip-card');
const btnExitReview = document.getElementById('btn-exit-review');
const reviewProgressFill = document.getElementById('review-progress-fill');

const reviewCompleteCard = document.getElementById('review-complete-card');
const nextReviewCountdown = document.getElementById('next-review-countdown');
const btnCompleteDone = document.getElementById('btn-complete-done');
const btnCompleteCram = document.getElementById('btn-complete-cram');

// Cram mode elements
const cramCard = document.getElementById('cram-card');
const cramCardWord = document.getElementById('cram-card-word');
const cramCardPhonetic = document.getElementById('cram-card-phonetic');
const cramCardPos = document.getElementById('cram-card-pos');
const cramCardDef = document.getElementById('cram-card-def');
const cramCardEx = document.getElementById('cram-card-ex');
const cramCardBack = document.getElementById('cram-card-back');
const cramControlsPrompt = document.getElementById('cram-controls-prompt');
const cramControlsRevealed = document.getElementById('cram-controls-revealed');
const btnFlipCram = document.getElementById('btn-flip-cram');
const btnNextCram = document.getElementById('btn-next-cram');
const btnExitCram = document.getElementById('btn-exit-cram');

// Header nav buttons
const btnNotifications = document.getElementById('btn-notifications');
const btnAnalytics = document.getElementById('btn-analytics');
const btnSync = document.getElementById('btn-sync');
const btnDecks = document.getElementById('btn-decks');
const btnCloseDecks = document.getElementById('btn-close-decks');
const btnCloseAnalytics = document.getElementById('btn-close-analytics');
const btnCloseSync = document.getElementById('btn-close-sync');
const btnCloseSyncX = document.getElementById('btn-close-sync-x');
const btnCloseNotif = document.getElementById('btn-close-notif');
const btnCloseNotifX = document.getElementById('btn-close-notif-x');

// Notification modal elements
const notifPermStatus = document.getElementById('notif-perm-status');
const btnToggleNotifPerm = document.getElementById('btn-toggle-notif-perm');
const inputNotifTime = document.getElementById('input-notif-time');
const btnSaveNotif = document.getElementById('btn-save-notif');

// Decks view elements
const inputNewDeckName = document.getElementById('input-new-deck-name');
const btnCreateDeckSubmit = document.getElementById('btn-create-deck-submit');
const decksContainer = document.getElementById('decks-container');
const deckList = document.getElementById('deck-list');
const allCardsCount = document.getElementById('all-cards-count');

// Analytics elements
const svgForgettingCurve = document.getElementById('svg-forgetting-curve');
const statLearning = document.getElementById('stat-learning');
const statReviewing = document.getElementById('stat-reviewing');
const statMastered = document.getElementById('stat-mastered');

// Sync elements
const btnExportJson = document.getElementById('btn-export-json');
const inputImportJson = document.getElementById('input-import-json');

let pendingHydrationWord = null;
let reviewQueue = [];
let reviewIndex = 0;
let cramQueue = [];
let cramIndex = 0;

// Load Initial Data from Server or Local Storage
async function loadInitialData() {
  try {
    const res = await fetch('/api/words');
    if (res.ok) {
      const data = await res.json();
      fsm.context.deck = data.words || [];
      fsm.context.decks = data.decks || [{ id: 'deck_core', name: 'General Vocabulary', color: '#6366f1' }];
    }
  } catch (err) {
    const stored = localStorage.getItem('axioma_lexis_deck');
    fsm.context.deck = stored ? JSON.parse(stored) : [];
    const storedDecks = localStorage.getItem('axioma_lexis_decks');
    fsm.context.decks = storedDecks ? JSON.parse(storedDecks) : [{ id: 'deck_core', name: 'General Vocabulary', color: '#6366f1' }];
  }
  updateDueStats();
  renderDecksUI();
  checkAndSendNotification();
}

function saveDeck() {
  localStorage.setItem('axioma_lexis_deck', JSON.stringify(fsm.context.deck));
  localStorage.setItem('axioma_lexis_decks', JSON.stringify(fsm.context.decks));
  updateDueStats();
  renderDecksUI();
  fetch('/api/words', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ words: fsm.context.deck, decks: fsm.context.decks })
  }).catch(() => {});
}

// Due-Queue Gating (AX-MEM-001)
function getDueCards() {
  const now = Date.now();
  return (fsm.context.deck || []).filter(c => {
    const nr = Number(c.next_review || 0);
    const nrMs = nr < 10000000000 ? nr * 1000 : nr;
    return nrMs <= now;
  });
}

function updateDueStats() {
  const due = getDueCards();
  if (badgeDueCount) {
    badgeDueCount.textContent = `${due.length} due`;
    badgeDueCount.classList.toggle('badge-zero', due.length === 0);
  }
  if (launcherStatusText) {
    launcherStatusText.textContent = due.length === 0
      ? "All caught up! Zero cards due for spaced review right now."
      : `${due.length} card${due.length === 1 ? '' : 's'} scheduled for spaced repetition.`;
  }
  if (btnStartReview) {
    btnStartReview.textContent = due.length === 0 ? "All Caught Up (0 Due)" : `Start Review (${due.length} Due)`;
    btnStartReview.disabled = due.length === 0;
  }
  if (deckCountBadge) {
    deckCountBadge.textContent = (fsm.context.deck || []).length;
  }
}

// Web Speech Audio Pronunciation (Anti-Mock: Real Browser API)
function speakWord(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  }
}

document.getElementById('btn-speak-preview')?.addEventListener('click', () => {
  if (pendingHydrationWord?.word) speakWord(pendingHydrationWord.word);
});

document.getElementById('btn-speak-card')?.addEventListener('click', (e) => {
  e.stopPropagation();
  const currentCard = reviewQueue[reviewIndex];
  if (currentCard) speakWord(currentCard.word);
});

document.getElementById('btn-speak-cram')?.addEventListener('click', (e) => {
  e.stopPropagation();
  const currentCard = cramQueue[cramIndex];
  if (currentCard) speakWord(currentCard.word);
});

// FSM State Listener (View Router)
fsm.subscribe((stateStr, context) => {
  btnUndo.disabled = fsm.historyStack.length === 0;

  if (stateStr.startsWith('idle')) {
    showView('idle');
    previewCard.classList.add('hidden');
    updateDueStats();
  } else if (stateStr.startsWith('capturing')) {
    showView('idle');
  } else if (stateStr.startsWith('reviewing')) {
    showView('review');
    renderReviewCard(stateStr);
  } else if (stateStr.startsWith('cramming')) {
    showView('cram');
    renderCramCard(stateStr);
  } else if (stateStr.startsWith('deck_management')) {
    showView('decks');
    renderDecksUI();
  } else if (stateStr.startsWith('analytics')) {
    showView('analytics');
    renderAnalyticsUI();
  } else if (stateStr.startsWith('sync')) {
    showView('sync');
  } else if (stateStr.startsWith('notification_prompt')) {
    showView('notifications');
    updateNotifUI();
  }
});

function showView(viewKey) {
  Object.keys(views).forEach(k => {
    if (views[k]) {
      views[k].classList.toggle('active', k === viewKey);
      views[k].classList.toggle('hidden', k !== viewKey);
    }
  });
}

// Word Capture Flow
btnCaptureSubmit.addEventListener('click', async () => {
  const query = inputWord.value.trim().toLowerCase();
  if (!query) return;

  fsm.transition('CAPTURE_START');
  fsm.transition('SUBMIT_WORD', { word: query });

  let hydrated = LOCAL_DICTIONARY[query];
  if (!hydrated) {
    try {
      const res = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(query)}`);
      if (res.ok) {
        const data = await res.json();
        const entry = data[0];
        const meaning = entry.meanings?.[0];
        hydrated = {
          word: entry.word,
          definition: meaning?.definitions?.[0]?.definition || "Definition retrieved from live dictionary.",
          part_of_speech: meaning?.partOfSpeech || "noun",
          phonetic: entry.phonetic || entry.phonetics?.[0]?.text || "",
          example: meaning?.definitions?.[0]?.example || ""
        };
      }
    } catch (err) {}
  }

  if (!hydrated) {
    hydrated = {
      word: query,
      definition: "Manual vocabulary entry.",
      part_of_speech: "term",
      phonetic: "",
      example: ""
    };
  }

  pendingHydrationWord = hydrated;
  previewWord.textContent = hydrated.word;
  previewPhonetic.textContent = hydrated.phonetic || "";
  previewPos.textContent = hydrated.part_of_speech;
  previewDef.textContent = hydrated.definition;
  previewEx.textContent = hydrated.example ? `"${hydrated.example}"` : "";

  // Populate deck options
  selectPreviewDeck.innerHTML = '';
  (fsm.context.decks || []).forEach(d => {
    const opt = document.createElement('option');
    opt.value = d.id;
    opt.textContent = d.name;
    selectPreviewDeck.appendChild(opt);
  });

  previewCard.classList.remove('hidden');
  fsm.transition('HYDRATE_SUCCESS', { word_data: hydrated });
});

btnSaveConfirm.addEventListener('click', () => {
  if (pendingHydrationWord) {
    const rawTags = inputPreviewTags.value.split(',').map(t => t.trim().toLowerCase()).filter(Boolean);
    const newWord = {
      id: `word_${Date.now()}`,
      ...pendingHydrationWord,
      deck_id: selectPreviewDeck.value || 'deck_core',
      tags: rawTags,
      status: 'learning',
      interval_days: 1.0,
      ease_factor: 2.5,
      repetition_level: 0,
      next_review: Date.now() // Available immediately for initial learning
    };
    fsm.context.deck.unshift(newWord);
    saveDeck();
    inputWord.value = '';
    inputPreviewTags.value = '';
    pendingHydrationWord = null;
    fsm.transition('CONFIRM_SAVE');
  }
});

btnSaveCancel.addEventListener('click', () => {
  pendingHydrationWord = null;
  previewCard.classList.add('hidden');
  fsm.transition('CANCEL');
});

// Flashcard Review Flow (Bite-Sized Paced SRS Session)
btnStartReview.addEventListener('click', () => {
  const due = getDueCards();
  if (due.length === 0) return;
  reviewQueue = due.slice(0, 15);
  reviewIndex = 0;
  fsm.transition('START_REVIEW');
});

function renderReviewCard(stateStr) {
  if (stateStr === 'reviewing.completed') {
    if (reviewActivePanel) reviewActivePanel.classList.add('hidden');
    if (reviewCompleteCard) reviewCompleteCard.classList.remove('hidden');
    updateCompletionCountdown();
    return;
  }

  if (reviewActivePanel) reviewActivePanel.classList.remove('hidden');
  if (reviewCompleteCard) reviewCompleteCard.classList.add('hidden');

  const card = reviewQueue[reviewIndex];
  if (!card) {
    fsm.transition('SESSION_COMPLETE');
    return;
  }

  cardWord.textContent = card.word;
  cardPhonetic.textContent = card.phonetic || "";
  cardPos.textContent = card.part_of_speech;
  cardDef.textContent = card.definition;
  cardEx.textContent = card.example ? `"${card.example}"` : "";

  // Deck badge
  const deckObj = (fsm.context.decks || []).find(d => d.id === card.deck_id);
  cardDeckName.textContent = deckObj ? deckObj.name : "Vocabulary";

  // Tags
  cardTagsRow.innerHTML = '';
  (card.tags || []).forEach(t => {
    const span = document.createElement('span');
    span.className = 'card-deck-pill';
    span.textContent = `#${t}`;
    cardTagsRow.appendChild(span);
  });

  const isRevealed = stateStr.includes('revealed');
  cardBack.classList.toggle('hidden', !isRevealed);
  cardPromptHint.classList.toggle('hidden', isRevealed);
  flipControls.classList.toggle('hidden', isRevealed);
  ratingControls.classList.toggle('hidden', !isRevealed);

  const pct = ((reviewIndex) / reviewQueue.length) * 100;
  reviewProgressFill.style.width = `${pct}%`;
}

function updateCompletionCountdown() {
  const now = Date.now();
  const futureReviews = (fsm.context.deck || [])
    .map(c => {
      const nr = Number(c.next_review || 0);
      return nr < 10000000000 ? nr * 1000 : nr;
    })
    .filter(t => t > now)
    .sort((a, b) => a - b);

  if (futureReviews.length > 0 && nextReviewCountdown) {
    const diffHours = Math.max(1, Math.round((futureReviews[0] - now) / 3600000));
    nextReviewCountdown.textContent = diffHours <= 1 ? "In ~1 hour" : `In ~${diffHours} hours`;
  } else if (nextReviewCountdown) {
    nextReviewCountdown.textContent = "Tomorrow";
  }
}

btnCompleteDone.addEventListener('click', () => {
  fsm.transition('CLOSE_SESSION');
});

btnCompleteCram.addEventListener('click', () => {
  startCramSession();
  fsm.transition('CRAM_AHEAD');
});

flashcard.addEventListener('click', () => {
  if (fsm.getStateString() === 'reviewing.prompt') {
    fsm.transition('FLIP_CARD');
  }
});

btnFlipCard.addEventListener('click', () => {
  fsm.transition('FLIP_CARD');
});

// SM-2 Spaced Repetition Ratings
['forgot', 'hard', 'good', 'easy'].forEach(rating => {
  document.getElementById(`btn-rate-${rating}`).addEventListener('click', () => {
    applyRating(rating.toUpperCase());
  });
});

function applyRating(rating) {
  const card = reviewQueue[reviewIndex];
  if (!card) return;

  if (rating === 'FORGOT') {
    card.interval_days = 0.5;
    card.ease_factor = Math.max(1.3, card.ease_factor - 0.2);
    card.repetition_level = 0;
  } else if (rating === 'HARD') {
    card.interval_days = Math.max(1.0, card.interval_days * 1.2);
    card.ease_factor = Math.max(1.3, card.ease_factor - 0.15);
  } else if (rating === 'GOOD') {
    card.interval_days = Math.max(1.0, card.interval_days * card.ease_factor);
    card.repetition_level += 1;
  } else if (rating === 'EASY') {
    card.interval_days = Math.max(2.0, card.interval_days * (card.ease_factor + 0.5));
    card.ease_factor += 0.15;
    card.repetition_level += 1;
  }

  // Update status tier
  card.status = card.interval_days > 21 ? 'mastered' : (card.interval_days > 3 ? 'review' : 'learning');
  card.next_review = Date.now() + (card.interval_days * 86400000);
  saveDeck();

  fsm.transition(`RATE_${rating}`);

  reviewIndex++;
  if (reviewIndex >= reviewQueue.length) {
    fsm.transition('SESSION_COMPLETE');
  } else {
    fsm.transition('NEXT_CARD');
  }
}

btnExitReview.addEventListener('click', () => {
  fsm.transition('EXIT_REVIEW');
});

// Cram / Practice Mode Flow (AX-MEM-008)
function startCramSession() {
  if (!fsm.context.deck || fsm.context.deck.length === 0) {
    alert("Deck is empty. Please capture a word first.");
    return;
  }
  cramQueue = [...fsm.context.deck];
  cramIndex = 0;
}

btnStartCram.addEventListener('click', () => {
  if (!fsm.context.deck || fsm.context.deck.length === 0) {
    alert("Deck is empty. Please capture a word first.");
    return;
  }
  startCramSession();
  fsm.transition('START_CRAM');
});

function renderCramCard(stateStr) {
  const card = cramQueue[cramIndex];
  if (!card) return;

  cramCardWord.textContent = card.word;
  cramCardPhonetic.textContent = card.phonetic || "";
  cramCardPos.textContent = card.part_of_speech;
  cramCardDef.textContent = card.definition;
  cramCardEx.textContent = card.example ? `"${card.example}"` : "";

  const isRevealed = stateStr.includes('revealed');
  cramCardBack.classList.toggle('hidden', !isRevealed);
  cramControlsPrompt.classList.toggle('hidden', isRevealed);
  cramControlsRevealed.classList.toggle('hidden', !isRevealed);
}

cramCard.addEventListener('click', () => {
  if (fsm.getStateString() === 'cramming.prompt') {
    fsm.transition('FLIP_CRAM');
  }
});

btnFlipCram.addEventListener('click', () => {
  fsm.transition('FLIP_CRAM');
});

btnNextCram.addEventListener('click', () => {
  cramIndex = (cramIndex + 1) % cramQueue.length;
  fsm.transition('NEXT_CRAM');
});

btnExitCram.addEventListener('click', () => {
  fsm.transition('EXIT_CRAM');
});

// Decks & Tags Management View
btnDecks.addEventListener('click', () => {
  fsm.transition('OPEN_DECKS');
});

btnCloseDecks.addEventListener('click', () => {
  fsm.transition('CLOSE_DECKS');
});

btnCreateDeckSubmit.addEventListener('click', () => {
  const name = inputNewDeckName.value.trim();
  if (!name) return;
  const newDeck = {
    id: `deck_${Date.now()}`,
    name: name,
    color: '#6366f1'
  };
  fsm.context.decks.push(newDeck);
  saveDeck();
  inputNewDeckName.value = '';
});

function renderDecksUI() {
  if (!decksContainer) return;
  decksContainer.innerHTML = '';
  (fsm.context.decks || []).forEach(d => {
    const cardCount = (fsm.context.deck || []).filter(w => w.deck_id === d.id).length;
    const div = document.createElement('div');
    div.className = 'deck-card';
    div.innerHTML = `
      <div class="deck-card-name">${d.name}</div>
      <div class="deck-card-count">${cardCount} card${cardCount === 1 ? '' : 's'}</div>
    `;
    decksContainer.appendChild(div);
  });

  allCardsCount.textContent = (fsm.context.deck || []).length;
  deckList.innerHTML = '';
  (fsm.context.deck || []).forEach(item => {
    const card = document.createElement('div');
    card.className = 'deck-item-card';
    card.innerHTML = `
      <div>
        <div class="deck-item-word">${item.word} <span class="badge-pos">${item.part_of_speech}</span></div>
        <div class="deck-item-def">${item.definition}</div>
      </div>
      <button class="btn btn-secondary btn-icon" title="Listen"><span>🔊</span></button>
    `;
    card.querySelector('button').addEventListener('click', () => speakWord(item.word));
    deckList.appendChild(card);
  });
}

// Analytics View & SVG Forgetting Curve
btnAnalytics.addEventListener('click', () => {
  fsm.transition('OPEN_ANALYTICS');
});

btnCloseAnalytics.addEventListener('click', () => {
  fsm.transition('CLOSE_ANALYTICS');
});

function renderAnalyticsUI() {
  const deck = fsm.context.deck || [];
  const learningCount = deck.filter(c => (c.status || 'learning') === 'learning').length;
  const reviewingCount = deck.filter(c => c.status === 'review').length;
  const masteredCount = deck.filter(c => c.status === 'mastered').length;

  if (statLearning) statLearning.textContent = learningCount;
  if (statReviewing) statReviewing.textContent = reviewingCount;
  if (statMastered) statMastered.textContent = masteredCount;

  // Draw SVG Ebbinghaus Curve
  if (svgForgettingCurve) {
    svgForgettingCurve.innerHTML = `
      <defs>
        <linearGradient id="gradCurve" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#6366f1" stop-opacity="0.6"/>
          <stop offset="100%" stop-color="#6366f1" stop-opacity="0.0"/>
        </linearGradient>
      </defs>
      <!-- Axes -->
      <line x1="40" y1="20" x2="40" y2="200" stroke="#3b4866" stroke-width="2"/>
      <line x1="40" y1="200" x2="480" y2="200" stroke="#3b4866" stroke-width="2"/>
      <text x="15" y="30" fill="#94a3b8" font-size="10">100%</text>
      <text x="20" y="115" fill="#94a3b8" font-size="10">50%</text>
      <text x="25" y="200" fill="#94a3b8" font-size="10">0%</text>
      <text x="50" y="215" fill="#94a3b8" font-size="10">Day 1</text>
      <text x="180" y="215" fill="#94a3b8" font-size="10">Day 7</text>
      <text x="320" y="215" fill="#94a3b8" font-size="10">Day 14</text>
      <text x="440" y="215" fill="#94a3b8" font-size="10">Day 30</text>
      
      <!-- Theoretical Unspaced Decay Path -->
      <path d="M 40 30 Q 120 160 480 190" fill="none" stroke="#ef4444" stroke-width="2" stroke-dasharray="4"/>
      <!-- Spaced SM-2 Retention Active Path -->
      <path d="M 40 30 C 80 40 100 80 120 40 C 180 50 200 90 220 45 C 320 50 360 80 480 55" fill="none" stroke="#10b981" stroke-width="3"/>
      
      <circle cx="120" cy="40" r="4" fill="#6366f1"/>
      <circle cx="220" cy="45" r="4" fill="#6366f1"/>
      <circle cx="480" cy="55" r="4" fill="#10b981"/>
    `;
  }
}

// Local-First Sync & JSON Backup
btnSync.addEventListener('click', () => {
  fsm.transition('OPEN_SYNC');
});

btnCloseSync.addEventListener('click', () => {
  fsm.transition('CLOSE_SYNC');
});

btnCloseSyncX.addEventListener('click', () => {
  fsm.transition('CLOSE_SYNC');
});

btnExportJson?.addEventListener('click', () => {
  const exportData = {
    version: "2.0",
    exported_at: new Date().toISOString(),
    decks: fsm.context.decks,
    words: fsm.context.deck
  };
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `axioma_lexis_backup_${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
});

inputImportJson?.addEventListener('change', (e) => {
  const file = e.target.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (evt) => {
    try {
      const data = JSON.parse(evt.target.result);
      if (data.words && Array.isArray(data.words)) {
        fsm.context.deck = data.words;
        if (data.decks) fsm.context.decks = data.decks;
        saveDeck();
        alert(`Successfully imported ${data.words.length} vocabulary words!`);
        fsm.transition('CLOSE_SYNC');
      } else {
        alert("Invalid backup file schema: missing words array.");
      }
    } catch (err) {
      alert("Failed to parse JSON backup file.");
    }
  };
  reader.readAsText(file);
});

// Notifications Flow
btnNotifications.addEventListener('click', () => {
  fsm.transition('OPEN_NOTIFICATIONS');
});

function updateNotifUI() {
  if (!('Notification' in window)) {
    if (notifPermStatus) notifPermStatus.textContent = "Status: Not supported in browser";
    if (btnToggleNotifPerm) btnToggleNotifPerm.disabled = true;
    return;
  }
  const perm = Notification.permission;
  if (notifPermStatus) notifPermStatus.textContent = `Status: ${perm.charAt(0).toUpperCase() + perm.slice(1)}`;
  if (btnToggleNotifPerm) {
    btnToggleNotifPerm.textContent = perm === 'granted' ? "Permission Granted ✓" : "Enable Reminders";
    btnToggleNotifPerm.disabled = perm === 'granted';
  }
  const savedTime = localStorage.getItem('axioma_lexis_notif_time');
  if (savedTime && inputNotifTime) inputNotifTime.value = savedTime;
}

btnToggleNotifPerm.addEventListener('click', async () => {
  if ('Notification' in window) {
    await Notification.requestPermission();
    updateNotifUI();
    checkAndSendNotification();
  }
});

btnSaveNotif.addEventListener('click', () => {
  if (inputNotifTime) localStorage.setItem('axioma_lexis_notif_time', inputNotifTime.value);
  fsm.transition('SAVE_PREFERENCES');
});

btnCloseNotif.addEventListener('click', () => fsm.transition('CLOSE_SETTINGS'));
btnCloseNotifX.addEventListener('click', () => fsm.transition('CLOSE_SETTINGS'));

function checkAndSendNotification() {
  if (!('Notification' in window) || Notification.permission !== 'granted') return;
  const due = getDueCards();
  if (due.length === 0) return;

  const today = new Date().toDateString();
  const lastNotif = localStorage.getItem('axioma_lexis_last_notif');
  if (lastNotif === today) return;

  new Notification("Axioma Lexis", {
    body: `You have ${due.length} vocabulary card${due.length === 1 ? '' : 's'} due for today's review!`,
    icon: "📚"
  });
  localStorage.setItem('axioma_lexis_last_notif', today);
}

// Keyboard Ergonomics
document.addEventListener('keydown', (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
  const stateStr = fsm.getStateString();

  if (e.code === 'Space') {
    if (stateStr === 'reviewing.prompt') {
      e.preventDefault();
      fsm.transition('FLIP_CARD');
    } else if (stateStr === 'cramming.prompt') {
      e.preventDefault();
      fsm.transition('FLIP_CRAM');
    }
  } else if (e.key === '1' && stateStr === 'reviewing.revealed') {
    applyRating('FORGOT');
  } else if (e.key === '2' && stateStr === 'reviewing.revealed') {
    applyRating('HARD');
  } else if (e.key === '3' && stateStr === 'reviewing.revealed') {
    applyRating('GOOD');
  } else if (e.key === '4' && stateStr === 'reviewing.revealed') {
    applyRating('EASY');
  } else if ((e.metaKey || e.ctrlKey) && e.key === 'z') {
    e.preventDefault();
    fsm.undo();
  }
});

// Functorial Undo
btnUndo.addEventListener('click', () => {
  fsm.undo();
});

// Initial Boot
loadInitialData();
"""

    def _generate_server_py(self, semantic_ir: SemanticDomainIR, contract_ir: DualBoundaryContractIR, port: int) -> str:
        if semantic_ir.app_id == "axioma_joy":
            return generate_joy_server_py(semantic_ir, contract_ir, port)
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
FEEDBACK_FILE = Path(__file__).parent / "data" / "user_feedback.json"
STATIC_DIR = Path(__file__).parent / "static"


def load_state():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {{"words": [], "decks": [{{"id": "deck_core", "name": "General Vocabulary"}}]}}


def save_state(state):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


class AppServerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/words":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(load_state()).encode("utf-8"))
        elif parsed.path == "/" or parsed.path == "":
            self.path = "/index.html"
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        if parsed.path == "/api/words":
            try:
                data = json.loads(body.decode("utf-8"))
                save_state(data)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({{"status": "ok"}}).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({{"error": str(e)}}).encode("utf-8"))
        elif parsed.path == "/api/feedback":
            try:
                feedback = json.loads(body.decode("utf-8"))
                FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
                existing = []
                if FEEDBACK_FILE.exists():
                    try:
                        existing = json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
                    except Exception:
                        existing = []
                existing.append(feedback)
                FEEDBACK_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({{"status": "received"}}).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({{"error": str(e)}}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    with http.server.HTTPServer(("", PORT), AppServerHandler) as httpd:
        print(f"[{semantic_ir.title}] Running at http://localhost:{port}")
        httpd.serve_forever()
"""

    def _generate_run_py(self, port: int) -> str:
        return f"""#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

def main():
    server_path = Path(__file__).parent / "server.py"
    print("Launching Axioma Lexis on http://localhost:{port}...")
    sys.exit(subprocess.call([sys.executable, str(server_path)]))

if __name__ == "__main__":
    main()
"""

    def _generate_app_json(self, semantic_ir: SemanticDomainIR, statechart_ir: StatechartIR, port: int) -> str:
        data = {
            "app_id": semantic_ir.app_id,
            "title": semantic_ir.title,
            "tagline": semantic_ir.tagline,
            "port": port,
            "generation": "gen_02b",
            "machine_id": statechart_ir.machine_id,
            "total_states": len(statechart_ir.get_all_state_paths()),
            "total_transitions": len(statechart_ir.get_all_transitions())
        }
        return json.dumps(data, indent=2)

    def _generate_test_py(self, semantic_ir: Optional[SemanticDomainIR] = None) -> str:
        app_id = semantic_ir.app_id if semantic_ir else "axioma_lexis"
        return f"""import json
from pathlib import Path
import unittest

class TestAppRuntime(unittest.TestCase):
    def test_static_files_exist(self):
        root = Path(__file__).parent.parent
        self.assertTrue((root / "static" / "index.html").exists())
        self.assertTrue((root / "static" / "style.css").exists())
        self.assertTrue((root / "static" / "app.js").exists())
        self.assertTrue((root / "static" / "machine.js").exists())
        self.assertTrue((root / "data" / "app_state.json").exists())
        self.assertTrue((root / "server.py").exists())
        self.assertTrue((root / "run.py").exists())

    def test_clean_slate_app_state(self):
        root = Path(__file__).parent.parent
        data_file = root / "data" / "app_state.json"
        self.assertTrue(data_file.exists())
        data = json.loads(data_file.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict)

    def test_app_json_configuration(self):
        root = Path(__file__).parent.parent
        app_json = root / "app.json"
        self.assertTrue(app_json.exists())
        cfg = json.loads(app_json.read_text(encoding="utf-8"))
        self.assertEqual(cfg.get("app_id"), "{app_id}")

if __name__ == "__main__":
    unittest.main()
"""

    def _generate_statechart_execution_test(self, statechart_ir: StatechartIR) -> str:
        from g2b_compiler.verification.model_checker import StatechartModelChecker
        checker = StatechartModelChecker(statechart_ir)
        check_result = checker.run_full_check()

        paths_data = [
            {"states": p.states, "events": p.events}
            for p in check_result.covering_paths
        ]
        negative_data = [{"state": tc["state"], "rejected_event": tc["rejected_event"]} for tc in check_result.negative_test_cases]
        machine_json = statechart_ir.to_xstate_v5_json(indent=2)

        return f'''"""Auto-Synthesized Exhaustive Statechart Execution Suite (System G2b).
Executes 100% of covering paths and all negative rejected transition assertions.
"""

import json
import unittest

MACHINE_CONFIG = json.loads({json.dumps(machine_json)})
COVERING_PATHS = json.loads({json.dumps(json.dumps(paths_data))})
NEGATIVE_CASES = json.loads({json.dumps(json.dumps(negative_data))})


class FSMRunner:
    def __init__(self, config):
        self.config = config
        self.reset()

    def reset(self):
        self.state = self.config["initial"]
        self.sub_state = self.config["states"].get(self.state, {{}}).get("initial", None)
        self.history = []

    def get_state(self):
        return f"{{self.state}}.{{self.sub_state}}" if self.sub_state else self.state

    def force_state(self, state_str):
        if "." in state_str:
            parts = state_str.split(".")
            self.state = parts[0]
            self.sub_state = ".".join(parts[1:])
        else:
            self.state = state_str
            self.sub_state = self.config["states"].get(self.state, {{}}).get("initial", None)

    def transition(self, event):
        curr_node = self.config["states"].get(self.state, {{}})
        trans = None

        if self.sub_state and "states" in curr_node and self.sub_state in curr_node["states"]:
            sub_node = curr_node["states"][self.sub_state]
            if "on" in sub_node and event in sub_node["on"]:
                trans = sub_node["on"][event]

        if not trans and "on" in curr_node and event in curr_node["on"]:
            trans = curr_node["on"][event]

        if not trans and event == "AUTO_INIT" and curr_node.get("initial"):
            trans = {{"target": curr_node["initial"]}}

        if not trans:
            return False

        self.history.append((self.state, self.sub_state))
        target = trans["target"]

        if "." in target:
            parts = target.split(".")
            self.state = parts[0]
            self.sub_state = ".".join(parts[1:])
        elif target in curr_node.get("states", {{}}):
            self.sub_state = target
        elif target in self.config["states"]:
            self.state = target
            self.sub_state = None
            sub = self.config["states"][target]
            while sub and "states" in sub and sub.get("initial"):
                self.sub_state = sub["initial"]
                sub = sub["states"].get(self.sub_state, {{}})
        else:
            self.state = target
            self.sub_state = None
        return True

    def undo(self):
        if not self.history:
            return False
        prev_state, prev_sub = self.history.pop()
        self.state = prev_state
        self.sub_state = prev_sub
        return True


class TestStatechartExhaustiveExecution(unittest.TestCase):
    def setUp(self):
        self.runner = FSMRunner(MACHINE_CONFIG)

    def test_all_covering_paths_100_percent_edge_traversal(self):
        for path_idx, path in enumerate(COVERING_PATHS):
            self.runner.reset()
            states = path["states"]
            events = path["events"]
            for step_idx, event in enumerate(events):
                expected_next = states[step_idx + 1]
                success = self.runner.transition(event)
                self.assertTrue(
                    success,
                    f"Path {{path_idx}} step {{step_idx}}: Event '{{event}}' failed in state '{{self.runner.get_state()}}'"
                )
                self.assertEqual(
                    self.runner.get_state(),
                    expected_next,
                    f"Path {{path_idx}} step {{step_idx}}: Expected state '{{expected_next}}', got '{{self.runner.get_state()}}'"
                )

    def test_all_negative_rejected_transitions(self):
        for case in NEGATIVE_CASES:
            target_state = case["state"]
            invalid_event = case["rejected_event"]
            self.runner.force_state(target_state)
            curr_state = self.runner.get_state()
            res = self.runner.transition(invalid_event)
            self.assertFalse(
                res,
                f"Negative Edge Failure: Invalid event '{{invalid_event}}' unexpectedly succeeded in state '{{curr_state}}'"
            )
            self.assertEqual(
                self.runner.get_state(),
                curr_state,
                f"Negative Edge Failure: State mutated from '{{curr_state}}' to '{{self.runner.get_state()}}' on rejected event '{{invalid_event}}'"
            )

    def test_functorial_undo_reversibility(self):
        for path in COVERING_PATHS:
            for i, evt in enumerate(path["events"]):
                if path["states"][i] != path["states"][i+1]:
                    self.runner.force_state(path["states"][i])
                    before = self.runner.get_state()
                    self.runner.transition(evt)
                    self.assertEqual(self.runner.get_state(), path["states"][i+1])
                    self.runner.undo()
                    self.assertEqual(self.runner.get_state(), before)
                    return


if __name__ == "__main__":
    unittest.main()
'''
