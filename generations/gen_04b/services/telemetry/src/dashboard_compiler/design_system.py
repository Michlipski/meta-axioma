"""Zero-CDN CSS Design System and Offline Math Engine for Sovereign Telemetry Dashboards ([L1-G3B-018], HERM-005, HERM-006)."""

from __future__ import annotations


def get_design_system_css() -> str:
    """Returns the complete, zero-CDN CSS stylesheet for the dashboard."""
    return """
    :root {
      --bg: #07090e;
      --bg-surface: rgba(13, 18, 30, 0.88);
      --bg-surface-elevated: rgba(20, 28, 48, 0.94);
      --border: rgba(255, 255, 255, 0.08);
      --border-bright: rgba(56, 189, 248, 0.35);
      --border-emerald: rgba(16, 185, 129, 0.35);
      --border-amber: rgba(245, 158, 11, 0.35);
      --border-rose: rgba(244, 63, 94, 0.35);
      --border-purple: rgba(168, 85, 247, 0.35);
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --cyan: #38bdf8;
      --cyan-glow: rgba(56, 189, 248, 0.25);
      --emerald: #10b981;
      --emerald-glow: rgba(16, 185, 129, 0.25);
      --amber: #f59e0b;
      --amber-glow: rgba(245, 158, 11, 0.25);
      --rose: #f43f5e;
      --rose-glow: rgba(244, 63, 94, 0.25);
      --purple: #a855f7;
      --purple-glow: rgba(168, 85, 247, 0.25);
      --indigo: #6366f1;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      --font-mono: "SF Mono", "Fira Code", Menlo, Monaco, Consolas, monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: var(--bg);
      background-image:
        radial-gradient(circle at 10% 12%, rgba(56, 189, 248, 0.08) 0%, transparent 45%),
        radial-gradient(circle at 88% 82%, rgba(168, 85, 247, 0.08) 0%, transparent 45%),
        radial-gradient(circle at 50% 48%, rgba(16, 185, 129, 0.04) 0%, transparent 60%);
      color: var(--text);
      font-family: var(--font-sans);
      min-height: 100vh;
      padding: 24px;
      line-height: 1.5;
    }

    /* Layout Containers */
    .dashboard-container {
      max-width: 1440px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    /* Header & Navigation Bar */
    header.dashboard-header {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      backdrop-filter: blur(16px);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .brand-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: linear-gradient(135deg, #0284c7, #10b981);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-size: 20px;
      letter-spacing: -0.5px;
      box-shadow: 0 0 20px rgba(56, 189, 248, 0.35);
      border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .title-area h1 {
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .title-area .subtitle {
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 4px;
      font-family: var(--font-mono);
    }

    .meta-pills {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    /* Badges */
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.3px;
      text-transform: uppercase;
      border: 1px solid transparent;
      font-family: var(--font-mono);
    }

    .badge-cyan {
      background: rgba(56, 189, 248, 0.12);
      color: var(--cyan);
      border-color: var(--border-bright);
      box-shadow: 0 0 10px var(--cyan-glow);
    }

    .badge-emerald {
      background: rgba(16, 185, 129, 0.12);
      color: var(--emerald);
      border-color: var(--border-emerald);
      box-shadow: 0 0 10px var(--emerald-glow);
    }

    .badge-amber {
      background: rgba(245, 158, 11, 0.12);
      color: var(--amber);
      border-color: var(--border-amber);
      box-shadow: 0 0 10px var(--amber-glow);
    }

    .badge-purple {
      background: rgba(168, 85, 247, 0.12);
      color: var(--purple);
      border-color: var(--border-purple);
      box-shadow: 0 0 10px var(--purple-glow);
    }

    .badge-rose {
      background: rgba(244, 63, 94, 0.12);
      color: var(--rose);
      border-color: var(--border-rose);
      box-shadow: 0 0 10px var(--rose-glow);
    }

    /* Top HUD Grid */
    .hud-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 16px;
    }

    .hud-card {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      position: relative;
      overflow: hidden;
      backdrop-filter: blur(12px);
      transition: border-color 0.2s, transform 0.2s;
    }

    .hud-card:hover {
      border-color: var(--border-bright);
      transform: translateY(-2px);
    }

    .hud-card::before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--cyan), transparent);
      opacity: 0.6;
    }

    .hud-label {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--text-muted);
      font-weight: 600;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .hud-val {
      font-size: 24px;
      font-weight: 800;
      letter-spacing: -0.5px;
      font-family: var(--font-mono);
      color: var(--text);
    }

    .hud-sub {
      font-size: 11px;
      color: var(--text-dim);
      margin-top: 6px;
      font-family: var(--font-mono);
    }

    /* Layout Grids */
    .layout-2col {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
      gap: 24px;
    }

    .layout-3col {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 20px;
    }

    /* Generic Cards */
    .card {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 24px;
      position: relative;
      backdrop-filter: blur(14px);
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
      flex-wrap: wrap;
      gap: 12px;
    }

    .card-title {
      font-size: 16px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .card-subtitle {
      font-size: 12px;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }

    /* Thermodynamic Donut Chart */
    .donut-wrapper {
      display: flex;
      align-items: center;
      gap: 28px;
      flex-wrap: wrap;
      justify-content: center;
      padding: 12px 0;
    }

    .donut-chart-svg {
      width: 170px;
      height: 170px;
      transform: rotate(-90deg);
    }

    .donut-bg {
      fill: none;
      stroke: rgba(255, 255, 255, 0.05);
      stroke-width: 20;
    }

    .donut-exploratory {
      fill: none;
      stroke: var(--cyan);
      stroke-width: 20;
      stroke-linecap: round;
      filter: drop-shadow(0 0 6px var(--cyan-glow));
    }

    .donut-protected {
      fill: none;
      stroke: var(--emerald);
      stroke-width: 20;
      stroke-linecap: round;
      filter: drop-shadow(0 0 6px var(--emerald-glow));
    }

    .donut-legend {
      display: flex;
      flex-direction: column;
      gap: 12px;
      flex: 1;
      min-width: 200px;
    }

    .legend-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 12px;
    }

    .legend-color-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      display: inline-block;
      margin-right: 8px;
    }

    /* Landauer Formula Card */
    .formula-display {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-bright);
      border-radius: 10px;
      padding: 14px 18px;
      font-family: var(--font-mono);
      font-size: 14px;
      color: var(--cyan);
      margin-bottom: 16px;
      text-align: center;
      box-shadow: 0 0 16px rgba(56, 189, 248, 0.1);
    }

    .dissipation-metrics-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }

    .dissipation-box {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
    }

    .dissipation-label {
      font-size: 11px;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .dissipation-val {
      font-size: 16px;
      font-weight: 700;
      font-family: var(--font-mono);
      margin-top: 4px;
    }

    /* Data Tables */
    .table-container {
      overflow-x: auto;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: rgba(0, 0, 0, 0.2);
    }

    table.data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      text-align: left;
    }

    table.data-table th {
      background: var(--bg-surface-elevated);
      color: var(--text-muted);
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
    }

    table.data-table td {
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
      vertical-align: middle;
    }

    table.data-table tr:last-child td {
      border-bottom: none;
    }

    table.data-table tr:hover td {
      background: rgba(255, 255, 255, 0.02);
    }

    .mono-cell {
      font-family: var(--font-mono);
      font-size: 12px;
    }

    /* Merkle Chain Timeline */
    .merkle-dag-container {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .merkle-block {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      transition: border-color 0.2s;
    }

    .merkle-block:hover {
      border-color: var(--border-bright);
    }

    .merkle-height {
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      padding: 4px 8px;
      background: rgba(56, 189, 248, 0.1);
      color: var(--cyan);
      border-radius: 6px;
      border: 1px solid var(--border-bright);
    }

    .merkle-info {
      flex: 1;
      min-width: 220px;
    }

    .merkle-title {
      font-size: 13px;
      font-weight: 600;
    }

    .merkle-hash {
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    /* Progress Bars */
    .progress-bar-container {
      width: 100%;
      height: 8px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 999px;
      overflow: hidden;
      margin-top: 6px;
    }

    .progress-bar-fill {
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--cyan), var(--emerald));
    }

    /* Topology SVG */
    .topology-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .topology-svg {
      width: 100%;
      height: 280px;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border);
      border-radius: 10px;
    }

    /* Footer */
    footer.dashboard-footer {
      border-top: 1px solid var(--border);
      padding: 24px 0 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      font-size: 12px;
      color: var(--text-dim);
      font-family: var(--font-mono);
    }

    /* Offline KaTeX Typography Support (HERM-006) */
    .katex {
      font-family: var(--font-mono), serif;
      font-size: 1.05em;
    }
    .katex-display {
      display: block;
      margin: 1em 0;
      text-align: center;
    }
    .katex-html {
      color: var(--cyan);
    }
    """


def get_offline_katex_script() -> str:
    """Returns the hermetic, zero-CDN offline KaTeX auto-render script hook."""
    return r"""
    // Hermetic offline KaTeX & Math Auto-Render engine definition (HERM-006)
    function renderMathInElement(elem, options) {
      if (!elem) return;
      try {
        const walker = document.createTreeWalker(elem, NodeFilter.SHOW_TEXT, null, false);
        let node;
        const nodesToProcess = [];
        while (node = walker.nextNode()) {
          if (node.parentElement && (
            node.parentElement.tagName === 'SCRIPT' ||
            node.parentElement.tagName === 'STYLE' ||
            node.parentElement.classList.contains('katex-rendered')
          )) {
            continue;
          }
          if (node.nodeValue && (node.nodeValue.includes('$') || node.nodeValue.includes('\\(') || node.nodeValue.includes('\\['))) {
            nodesToProcess.push(node);
          }
        }
        nodesToProcess.forEach(n => {
          const span = document.createElement('span');
          span.className = 'katex-rendered';
          span.innerHTML = n.nodeValue
            .replace(/\$\$([^$]+)\$\$/g, '<div class="katex-display"><span class="katex"><span class="katex-html font-mono" style="color:var(--cyan);">$1</span></span></div>')
            .replace(/\$([^$]+)\$/g, '<span class="katex"><span class="katex-html font-mono" style="color:var(--cyan);">$1</span></span>');
          if (n.parentNode) n.parentNode.replaceChild(span, n);
        });
      } catch (e) {
        console.warn("KaTeX offline render warning:", e);
      }
    }

    function initKaTeX() {
      if (typeof renderMathInElement === 'function') {
        try {
          renderMathInElement(document.body, {
            delimiters: [
              {left: '$$', right: '$$', display: true},
              {left: '$', right: '$', display: false},
              {left: '\\[', right: '\\]', display: true},
              {left: '\\(', right: '\\)', display: false}
            ],
            throwOnError: false
          });
        } catch (err) {
          console.warn('KaTeX init error:', err);
        }
      }
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initKaTeX);
    } else {
      initKaTeX();
    }
    """
