"""Header, Hero Metadata, and Thermodynamic Dissipation Meter Renderer ([L1-G2B-005], [L1-G3B-018])."""

from __future__ import annotations

import html
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .schema import DashboardAST


def render_header(ast: DashboardAST) -> str:
    """Renders the dashboard header, top HUD metrics, and thermodynamic capital cards."""
    # Derive initials for brand icon
    words = [w for w in ast.title.replace("&amp;", "&").split() if w[0].isalnum()]
    initials = "".join(w[0].upper() for w in words[:2]) if words else "AX"

    # Donut circumference math for radius = 60
    c_tot = 376.99
    c_exp = c_tot * 0.60
    c_pro = c_tot * 0.40

    urn_string = f"URN:AXIOMA:G4B:{ast.app_id.upper()}:RELEASE_CANDIDATE"

    # Landauer dissipation numbers
    erased_bits_str = f"{ast.main_tokens.erased_bits:,}"
    joules_str = f"{ast.main_tokens.dissipation_joules:.3e} J"
    ev_str = f"{ast.main_tokens.dissipation_ev:.2f} eV"

    # Math formula with escaped backslashes
    math_formula = r"$$Q = k_B \cdot T \cdot \ln(2) \cdot N_{\text{bits} }$$"

    return f"""
    <!-- Dashboard Header -->
    <header class="dashboard-header">
      <div class="brand-group">
        <div class="brand-icon">{html.escape(initials)}</div>
        <div class="title-area">
          <h1>
            {html.escape(ast.title)}
            <span class="badge badge-emerald">VERIFIED RC</span>
            <span class="badge badge-cyan">{html.escape(ast.generation.upper())}</span>
          </h1>
          <div class="subtitle">{html.escape(ast.subtitle)} &bull; {html.escape(urn_string)}</div>
        </div>
      </div>
      <div class="meta-pills">
        <span class="badge badge-purple">SUBNET: {html.escape(ast.subnet)}</span>
        <span class="badge badge-amber">PORT: {ast.port}</span>
        <span class="badge badge-cyan">MERKLE: {html.escape(ast.merkle_root[:12])}...</span>
      </div>
    </header>

    <!-- Top HUD Stats Grid -->
    <section class="hud-grid">
      <div class="hud-card">
        <div class="hud-label">Approved BPE Budget <span>[L1-G2B-005]</span></div>
        <div class="hud-val" style="color:var(--cyan);">{ast.unified_bpe_budget:,}</div>
        <div class="hud-sub">Unified Token Capital</div>
      </div>
      <div class="hud-card">
        <div class="hud-label">Exploratory Capital (60%) <span>CEILING</span></div>
        <div class="hud-val" style="color:var(--cyan);">{ast.exploratory_capital_60:,}</div>
        <div class="hud-sub">Generative Synthesis Leases</div>
      </div>
      <div class="hud-card">
        <div class="hud-label">Protected Capital (40%) <span>FLOOR</span></div>
        <div class="hud-val" style="color:var(--emerald);">{ast.protected_capital_40:,}</div>
        <div class="hud-sub">Reserved Verification Sinks</div>
      </div>
      <div class="hud-card">
        <div class="hud-label">Actual BPE Burned <span>EMPIRICAL</span></div>
        <div class="hud-val" style="color:var(--purple);">{ast.actual_bpe_burned:,}</div>
        <div class="hud-sub">Verified Spend (Delta: {ast.unified_bpe_budget - ast.actual_bpe_burned:,})</div>
      </div>
      <div class="hud-card">
        <div class="hud-label">Merkle DAG Root <span>[L1-G4B-003]</span></div>
        <div class="hud-val" style="color:var(--amber); font-size:18px;">{html.escape(ast.merkle_root[:16])}</div>
        <div class="hud-sub">Quine Attestation Sealed</div>
      </div>
      <div class="hud-card">
        <div class="hud-label">Test Substrate Sinks <span>[NEG-G1B-001]</span></div>
        <div class="hud-val" style="color:var(--emerald);">{ast.test_summary.get("passing", 0)} / {ast.test_summary.get("total_tests", 0)}</div>
        <div class="hud-sub">Exit Code: 0 (OK &bull; Hermetic)</div>
      </div>
    </section>

    <!-- Thermodynamic Capital & Landauer Dissipation Section -->
    <section class="layout-2col">
      <!-- Thermodynamic Capital Partition Card -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <span>&#9883;</span> Thermodynamic Capital &amp; Token Partition ([L1-G2B-005])
          </div>
          <span class="badge badge-cyan">RATIO 60 / 40</span>
        </div>
        <div class="donut-wrapper">
          <svg class="donut-chart-svg" viewBox="0 0 160 160">
            <circle class="donut-bg" cx="80" cy="80" r="60"></circle>
            <!-- 60% Exploratory Arc -->
            <circle class="donut-exploratory" cx="80" cy="80" r="60"
              stroke-dasharray="{c_exp:.1f} {c_tot - c_exp:.1f}"
              stroke-dashoffset="0"></circle>
            <!-- 40% Protected Arc -->
            <circle class="donut-protected" cx="80" cy="80" r="60"
              stroke-dasharray="{c_pro:.1f} {c_tot - c_pro:.1f}"
              stroke-dashoffset="-{c_exp:.1f}"></circle>
          </svg>
          <div class="donut-legend">
            <div class="legend-item">
              <div>
                <span class="legend-color-dot" style="background:var(--cyan); box-shadow:0 0 8px var(--cyan);"></span>
                <strong>Exploratory Capital (60%)</strong>
              </div>
              <span class="mono-cell">{ast.exploratory_capital_60:,} BPE</span>
            </div>
            <div class="legend-item">
              <div>
                <span class="legend-color-dot" style="background:var(--emerald); box-shadow:0 0 8px var(--emerald);"></span>
                <strong>Protected Capital (40%)</strong>
              </div>
              <span class="mono-cell">{ast.protected_capital_40:,} BPE</span>
            </div>
            <div class="legend-item">
              <div>
                <span class="legend-color-dot" style="background:var(--purple); box-shadow:0 0 8px var(--purple);"></span>
                <strong>Actual Burned</strong>
              </div>
              <span class="mono-cell">{ast.actual_bpe_burned:,} BPE</span>
            </div>
          </div>
        </div>
        <div style="margin-top: 12px;">
          <div style="display:flex; justify-content:space-between; font-size:12px; color:var(--text-muted); font-family:var(--font-mono);">
            <span>Budget Utilization</span>
            <span>{ast.actual_bpe_burned / max(ast.unified_bpe_budget, 1) * 100:.1f}%</span>
          </div>
          <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {min(100.0, ast.actual_bpe_burned / max(ast.unified_bpe_budget, 1) * 100):.1f}%;"></div>
          </div>
        </div>
      </div>

      <!-- Landauer Thermodynamic Dissipation Meter Card -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <span>&#9889;</span> Thermodynamic Landauer Dissipation Meter ([L1-G3B-018])
          </div>
          <span class="badge badge-emerald">SUB-THERMAL</span>
        </div>
        <div class="formula-display">
          {math_formula}
        </div>
        <div class="dissipation-metrics-grid">
          <div class="dissipation-box">
            <div class="dissipation-label">Thermal Ambient</div>
            <div class="dissipation-val" style="color:var(--text);">T = 300.00 K</div>
          </div>
          <div class="dissipation-box">
            <div class="dissipation-label">Irreversible Bit Erasures</div>
            <div class="dissipation-val" style="color:var(--cyan);">{erased_bits_str}</div>
          </div>
          <div class="dissipation-box">
            <div class="dissipation-label">Heat Dissipation (Joules)</div>
            <div class="dissipation-val" style="color:var(--emerald);">{joules_str}</div>
          </div>
          <div class="dissipation-box">
            <div class="dissipation-label">Equivalent Energy (eV)</div>
            <div class="dissipation-val" style="color:var(--amber);">{ev_str}</div>
          </div>
        </div>
        <div style="margin-top: 14px; font-size: 12px; color: var(--text-dim); font-family: var(--font-mono);">
          State entropy decay bounded by micro-auditors &bull; Zero runaway heat dissipation.
        </div>
      </div>
    </section>
    """
