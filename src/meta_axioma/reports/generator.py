"""Epoch report generator: saves persistent JSON/Markdown telemetry and builds an interactive HTML UI dashboard."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from meta_axioma.types import (
    Axiom,
    AxiomLevel,
    AxiomStatus,
    EpochTelemetry,
    NegativeAxiom,
    PhaseState,
)


class EpochReportGenerator:
    """Saves structured epoch telemetry and compiles an interactive HTML dashboard."""

    def __init__(self, reports_dir: Optional[Path] = None, artifact_dir: Optional[Path] = None):
        if reports_dir is None:
            # Default to active generation epochs
            self.reports_dir = Path(__file__).resolve().parent.parent.parent.parent / "generations" / "gen_01" / "epochs"
        else:
            self.reports_dir = reports_dir

        self.data_dir = self.reports_dir / "data"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.artifact_dir = artifact_dir or self.reports_dir

    def initialize_baseline_report(
        self,
        active_axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
        efficacy: float = 1.0,
    ) -> Path:
        """Creates the initial Epoch 0 baseline report and builds dashboard.html."""
        dashboard_path = self.reports_dir / "dashboard.html"
        all_epochs = self._load_all_epoch_records()
        html_content = self._render_dashboard_html(
            current_telemetry=None,
            all_epochs=all_epochs,
            active_axioms=active_axioms,
            negative_axioms=negative_axioms,
        )
        dashboard_path.write_text(html_content, encoding="utf-8")
        if self.reports_dir.name == "epochs" and self.reports_dir.parent.exists():
            try:
                (self.reports_dir.parent / "dashboard.html").write_text(html_content, encoding="utf-8")
            except Exception:
                pass

        try:
            if self.artifact_dir.exists():
                artifact_dash = self.artifact_dir / "dashboard.html"
                artifact_dash.write_text(html_content, encoding="utf-8")
        except Exception:
            pass

        return dashboard_path

    def save_epoch_report(
        self,
        telemetry: EpochTelemetry,
        active_axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
    ) -> Path:
        """Saves JSON snapshot, markdown summary, and rebuilds the HTML dashboard."""
        epoch = telemetry.epoch
        json_path = self.data_dir / f"epoch_{epoch:03d}.json"
        md_path = self.reports_dir / f"epoch_{epoch:03d}.md"

        # Serialize JSON
        data = {
            "epoch": epoch,
            "timestamp": telemetry.timestamp,
            "phase": telemetry.phase.value,
            "current_efficacy": telemetry.current_efficacy,
            "efficacy_derivative": telemetry.efficacy_derivative,
            "active_l0_count": telemetry.active_l0_count,
            "active_l1_count": telemetry.active_l1_count,
            "total_active": telemetry.total_active,
            "compute_budget": telemetry.compute_budget.__dict__,
            "candidate_axiom": telemetry.candidate_axiom.to_dict() if telemetry.candidate_axiom else None,
            "tri_fold_metrics": telemetry.tri_fold_metrics.__dict__ if telemetry.tri_fold_metrics else None,
            "user_candidate": telemetry.user_candidate.to_dict() if telemetry.user_candidate else None,
            "user_metrics": telemetry.user_metrics.__dict__ if telemetry.user_metrics else None,
            "comparative_summary": telemetry.comparative_summary,
            "candidate_pool": [c.to_dict() for c in telemetry.candidate_pool] if telemetry.candidate_pool else None,
            "tournament_leaderboard": telemetry.tournament_leaderboard,
            "decision": telemetry.decision,
            "jettison_triggered": telemetry.jettison_triggered,
        }

        json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        # Write markdown summary
        md_content = self._render_markdown_report(telemetry, active_axioms, negative_axioms)
        md_path.write_text(md_content, encoding="utf-8")

        # Compile and refresh master dashboard
        dashboard_path = self.reports_dir / "dashboard.html"
        all_epochs = self._load_all_epoch_records()
        html_content = self._render_dashboard_html(
            current_telemetry=telemetry,
            all_epochs=all_epochs,
            active_axioms=active_axioms,
            negative_axioms=negative_axioms,
        )
        dashboard_path.write_text(html_content, encoding="utf-8")
        if self.reports_dir.name == "epochs" and self.reports_dir.parent.exists():
            try:
                (self.reports_dir.parent / "dashboard.html").write_text(html_content, encoding="utf-8")
            except Exception:
                pass

        # Also write to brain artifact directory if it exists
        try:
            if self.artifact_dir.exists():
                artifact_dash = self.artifact_dir / "dashboard.html"
                artifact_dash.write_text(html_content, encoding="utf-8")
        except Exception:
            pass

        return json_path

    def _load_all_epoch_records(self) -> List[Dict[str, Any]]:
        """Loads all historical epoch JSON records sorted by epoch number."""
        records = []
        for file in sorted(self.data_dir.glob("epoch_*.json")):
            try:
                rec = json.loads(file.read_text(encoding="utf-8"))
                records.append(rec)
            except Exception:
                continue
        return records

    def _render_system_breakdown_markdown(self, cand_item: Dict[str, Any]) -> List[str]:
        prof = cand_item.get("system_profile") or {}
        lines = []
        c_id = cand_item.get("id", "-")
        c_name = cand_item.get("name", "Unnamed Axiom")
        c_level = cand_item.get("level", "LEVEL_0_EPISTEMIC")
        c_domain = cand_item.get("domain", "General Systems")
        c_principle = cand_item.get("principle", "")
        agg = cand_item.get("aggregate_delta_e", 0.0)

        lines.append(f"### System Architecture Profile: [{c_id}] {c_name}")
        lines.append(f"- **Tier:** `{c_level}` | **Domain:** {c_domain} (*{c_principle}*)")
        lines.append(f"- **Aggregate Efficacy Impact:** $\\Delta E = {agg:+.4f}$")
        if cand_item.get("statement"):
            lines.append(f"- **Core Invariant:** {cand_item.get('statement')}")
        if cand_item.get("operational_rule"):
            lines.append(f"- **Operational Compiler Rule:** `{cand_item.get('operational_rule')}`")
        if cand_item.get("formal_expression"):
            lines.append(f"- **Formal Specification:** $${cand_item.get('formal_expression')}$$")

        archetype = prof.get("archetype", f"Compiled System Archetype ({c_id})")
        top_type = prof.get("topology_type", "Decoupled Component Mesh")
        lines.append("")
        lines.append(f"#### 1. Compiled System Archetype & Topology")
        lines.append(f"- **Archetype Name:** `{archetype}`")
        lines.append(f"- **Topology Class:** `{top_type}`")

        diag = prof.get("topology_diagram")
        if diag:
            lines.append("```text")
            lines.append(diag.strip())
            lines.append("```")

        subs = prof.get("subsystems")
        if subs and isinstance(subs, dict):
            lines.append("#### 2. Synthesized Subsystem Components & Invariant Enforcement")
            for sub_name, sub_info in subs.items():
                if isinstance(sub_info, dict):
                    role = sub_info.get("role", "")
                    inv = sub_info.get("invariant_rule", "")
                    lines.append(f"- **`{sub_name}`**:")
                    lines.append(f"  - *Architectural Role:* {role}")
                    lines.append(f"  - *Enforced Invariant:* {inv}")
                else:
                    lines.append(f"- **`{sub_name}`**: {sub_info}")

        behaviors = prof.get("target_behaviors")
        if behaviors and isinstance(behaviors, dict):
            lines.append("")
            lines.append("#### 3. Target Simulation Dynamics & Behavioral Profile")
            for t_key, t_desc in behaviors.items():
                t_label = t_key.replace("target_", "Target ").replace("_", " ").title()
                lines.append(f"- **{t_label}:** {t_desc}")

        tradeoffs = prof.get("tradeoffs")
        if tradeoffs and isinstance(tradeoffs, dict):
            lines.append("")
            lines.append("#### 4. Structural Trade-offs & Invariant Impact")
            if "strengths" in tradeoffs:
                lines.append(f"- **Guaranteed Strengths:** {tradeoffs['strengths']}")
            if "constraints" in tradeoffs:
                lines.append(f"- **Operational Constraints:** {tradeoffs['constraints']}")

        lines.append("")
        return lines

    def _render_markdown_report(
        self,
        t: EpochTelemetry,
        active_axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
    ) -> str:
        lines = [
            f"# Epoch {t.epoch} Telemetry Report",
            f"- **Timestamp:** {t.timestamp}",
            f"- **Phase:** `{t.phase.value}`",
            f"- **Global Efficacy ($E$):** `{t.current_efficacy:.4f}` ($\\frac{{dE}}{{dt}} = {t.efficacy_derivative:+.4f}$)",
            f"- **Compute Allocation:** `{t.compute_budget.token_budget:,}` tokens | Depth: `{t.compute_budget.simulation_depth}` (Active $n={t.total_active}$)",
            f"- **Resolution:** `{t.decision}`",
            "",
            "## Evaluated Candidates",
        ]

        if t.candidate_axiom and t.tri_fold_metrics:
            outcomes_str = f"$\\Delta E_1={t.tri_fold_metrics.delta_e1:+.4f}$, $\\Delta E_2={t.tri_fold_metrics.delta_e2:+.4f}$, $\\Delta E_3={t.tri_fold_metrics.delta_e3:+.4f}$"
            if getattr(t.tri_fold_metrics, "delta_e4", 0.0):
                outcomes_str += f", $\\Delta E_4={t.tri_fold_metrics.delta_e4:+.4f}$"
            lines.extend([
                f"### Primary Candidate: [{t.candidate_axiom.id}] {t.candidate_axiom.name}",
                f"- **Statement:** {t.candidate_axiom.statement}",
                f"- **Rule:** {t.candidate_axiom.operational_rule}",
                f"- **Validation Outcomes:** {outcomes_str}",
                f"- **Aggregate Delta:** $\\Delta E = {t.tri_fold_metrics.aggregate_delta_e:+.4f}$",
                "",
            ])

        if t.user_candidate and t.user_metrics:
            u_outcomes_str = f"$\\Delta E_1={t.user_metrics.delta_e1:+.4f}$, $\\Delta E_2={t.user_metrics.delta_e2:+.4f}$, $\\Delta E_3={t.user_metrics.delta_e3:+.4f}$"
            if getattr(t.user_metrics, "delta_e4", 0.0):
                u_outcomes_str += f", $\\Delta E_4={t.user_metrics.delta_e4:+.4f}$"
            lines.extend([
                f"### User Seed: [{t.user_candidate.id}] {t.user_candidate.name}",
                f"- **Statement:** {t.user_candidate.statement}",
                f"- **Rule:** {t.user_candidate.operational_rule}",
                f"- **Validation Outcomes:** {u_outcomes_str}",
                f"- **Aggregate Delta:** $\\Delta E = {t.user_metrics.aggregate_delta_e:+.4f}$",
                "",
            ])

        if t.tournament_leaderboard and len(t.tournament_leaderboard) > 1:
            has_e4 = any(item.get("delta_e4", 0.0) != 0.0 for item in t.tournament_leaderboard)
            if has_e4:
                lines.extend([
                    "## Autonomous Multi-Candidate Tournament Leaderboard",
                    "| Rank | Candidate | Domain | ΔE₁ | ΔE₂ | ΔE₃ | ΔE₄ (UX) | Aggregate ΔE | Status |",
                    "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
                ])
                for idx, item in enumerate(t.tournament_leaderboard, 1):
                    status = "🏆 Winner" if idx == 1 and item.get("is_strictly_improving") else "Outperformed"
                    lines.append(
                        f"| `{idx}` | [{item.get('id')}] {item.get('name')} | {item.get('domain', '-')} | "
                        f"{item.get('delta_e1', 0):+.4f} | {item.get('delta_e2', 0):+.4f} | {item.get('delta_e3', 0):+.4f} | {item.get('delta_e4', 0):+.4f} | "
                        f"**{item.get('aggregate_delta_e', 0):+.4f}** | {status} |"
                    )
            else:
                lines.extend([
                    "## Autonomous Multi-Candidate Tournament Leaderboard",
                    "| Rank | Candidate | Domain | ΔE₁ | ΔE₂ | ΔE₃ | Aggregate ΔE | Status |",
                    "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
                ])
                for idx, item in enumerate(t.tournament_leaderboard, 1):
                    status = "🏆 Winner" if idx == 1 and item.get("is_strictly_improving") else "Outperformed"
                    lines.append(
                        f"| `{idx}` | [{item.get('id')}] {item.get('name')} | {item.get('domain', '-')} | "
                        f"{item.get('delta_e1', 0):+.4f} | {item.get('delta_e2', 0):+.4f} | {item.get('delta_e3', 0):+.4f} | "
                        f"**{item.get('aggregate_delta_e', 0):+.4f}** | {status} |"
                    )
            lines.append("")


        elif t.comparative_summary and t.comparative_summary.get("llm_aggregate_delta_e") is not None:
            s = t.comparative_summary
            lines.extend([
                "## Comparative Tournament Summary",
                f"- **LLM $\\Delta E$:** `{s.get('llm_aggregate_delta_e'):+.4f}`",
                f"- **User $\\Delta E$:** `{s.get('user_aggregate_delta_e'):+.4f}`",
                f"- **Delta Difference ($\\Delta\\Delta E$):** `{s.get('delta_diff', 0):+.4f}` (Winner: {'User Seed' if s.get('user_won') else 'LLM Candidate'})",
                "",
            ])

        # Detailed Breakdowns of Evaluated Systems
        lines.append("## Evaluated Systems & Architectural Breakdowns")
        lines.append("*Detailed structural and epistemic breakdowns of systems compiled under each candidate hypothesis:*")
        lines.append("")

        if t.tournament_leaderboard:
            for item in t.tournament_leaderboard:
                lines.extend(self._render_system_breakdown_markdown(item))
        elif t.candidate_axiom:
            cand_dict = {
                "id": t.candidate_axiom.id,
                "name": t.candidate_axiom.name,
                "level": t.candidate_axiom.level.value,
                "statement": t.candidate_axiom.statement,
                "formal_expression": t.candidate_axiom.formal_expression,
                "operational_rule": t.candidate_axiom.operational_rule,
                "domain": t.candidate_axiom.metadata.get("exogenous_domain", ""),
                "principle": t.candidate_axiom.metadata.get("source_principle", ""),
                "aggregate_delta_e": t.tri_fold_metrics.aggregate_delta_e if t.tri_fold_metrics else 0.0,
                "system_profile": t.candidate_axiom.metadata.get("system_profile", {}),
            }
            lines.extend(self._render_system_breakdown_markdown(cand_dict))
            if t.user_candidate:
                user_dict = {
                    "id": t.user_candidate.id,
                    "name": t.user_candidate.name,
                    "level": t.user_candidate.level.value,
                    "statement": t.user_candidate.statement,
                    "formal_expression": t.user_candidate.formal_expression,
                    "operational_rule": t.user_candidate.operational_rule,
                    "domain": t.user_candidate.metadata.get("exogenous_domain", "Operator Injected"),
                    "principle": t.user_candidate.metadata.get("source_principle", "Human Structural Seed"),
                    "aggregate_delta_e": t.user_metrics.aggregate_delta_e if t.user_metrics else 0.0,
                    "system_profile": t.user_candidate.metadata.get("system_profile", {}),
                }
                lines.extend(self._render_system_breakdown_markdown(user_dict))

        if t.lookahead_analysis:
            la = t.lookahead_analysis
            jb = la.get("jettison_branch", {})
            rb = la.get("retain_branch", {})
            rec = la.get("recommendation", "INCONCLUSIVE")
            conf = la.get("confidence_score", 0.5)
            net_diff = la.get("net_lookahead_differential", 0.0)
            tok_div = la.get("compute_dividend_tokens", 0)
            depth_div = la.get("compute_dividend_depth", 0)
            risk = la.get("risk_assessment", {})

            lines.extend([
                "## Axiom Lookahead & Speculative Horizon Analysis (The Jettison Radar)",
                f"- **Lookahead Horizon ($H$):** `{la.get('lookahead_horizon', 2)}` epochs forward",
                f"- **Compiler Recommendation:** **`{rec}`** (Confidence: `{conf * 100:.0f}%`)",
                f"- **Net Speculative Differential ($\\Lambda_H$):** `{net_diff:+.4f}`",
                f"- **Compute Dividend Unlocked by Jettison:** `+{tok_div:,}` tokens/epoch | `+{depth_div}` simulation depth",
                "",
                "### Dual-Branch Speculative Trajectory Comparison",
                "| Metric / Parameter | Branch A: Speculative Jettison | Branch B: Retain Epistemic Scaffolding | Differential / Advantage |",
                "| :--- | :--- | :--- | :--- |",
                f"| Active Invariants ($n$) | `{jb.get('active_axiom_count', 0)}` structural | `{rb.get('active_axiom_count', 0)}` total | `{rb.get('active_axiom_count', 0) - jb.get('active_axiom_count', 0)}` fewer invariants |",
                f"| Compute Tokens per Epoch | `{jb.get('tokens', 0):,}` tokens | `{rb.get('tokens', 0):,}` tokens | **`+{tok_div:,}` tokens** |",
                f"| Simulation Depth Limit | `{jb.get('depth', 0)}` steps | `{rb.get('depth', 0)}` steps | **`+{depth_div}` depth levels** |",
                f"| Projected Cumulative $\\Delta E$ | **`{jb.get('projected_cumulative_delta', 0):+.4f}`** | **`{rb.get('projected_cumulative_delta', 0):+.4f}`** | **`{net_diff:+.4f}`** {'(Jettison Edge)' if net_diff > 0 else '(Retain Edge)'} |",
                f"| Mean $\\Delta E$ per Epoch | `{jb.get('mean_delta_per_epoch', 0):+.4f}` | `{rb.get('mean_delta_per_epoch', 0):+.4f}` | `{jb.get('mean_delta_per_epoch', 0) - rb.get('mean_delta_per_epoch', 0):+.4f}` |",
                "",
                "#### Speculative Branch Rationales",
                f"- **Branch A (Jettison):** {jb.get('rationale', '')}",
                f"- **Branch B (Retain):** {rb.get('rationale', '')}",
                "",
                "#### Risk & Lineage Assessment",
                f"- **Compute Starvation Risk:** {risk.get('compute_starvation_risk', '-')}",
                f"- **Epistemic Drift Risk:** {risk.get('epistemic_drift_risk', '-')}",
                f"- **Invariant Lineage Preservation:** {risk.get('invariant_lineage_preservation', '-')}",
                "",
            ])

        active_only = [a for a in active_axioms if a.status == AxiomStatus.ACTIVE]
        inactive_only = [a for a in active_axioms if a.status in (AxiomStatus.INACTIVE, AxiomStatus.PRUNED)]

        lines.extend([
            "## Active Axiom Set",
            f"Total Active: {len(active_only)}",
        ])
        for ax in active_only:
            lines.append(f"- `[{ax.id}]` ({ax.level.value}): {ax.name}")

        if inactive_only:
            lines.extend([
                "",
                "## Inactive Epistemic Scaffolding (Retained Lineage)",
                f"Total Inactive: {len(inactive_only)}",
            ])
            for ax in inactive_only:
                lines.append(f"- `[{ax.id}]` ({ax.level.value}): {ax.name} *(Deactivated in Epoch {ax.metadata.get('jettisoned_at_epoch', ax.origin_epoch)})*")

        return "\n".join(lines) + "\n"

    def _render_dashboard_html(
        self,
        current_telemetry: Optional[EpochTelemetry],
        all_epochs: List[Dict[str, Any]],
        active_axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
    ) -> str:
        """Renders an interactive HTML dashboard using Tailwind CSS and semantic variables."""
        cur_epoch = current_telemetry.epoch if current_telemetry else (all_epochs[-1]["epoch"] if all_epochs else 0)
        cur_eff = current_telemetry.current_efficacy if current_telemetry else (all_epochs[-1]["current_efficacy"] if all_epochs else 1.0)
        cur_phase = current_telemetry.phase.value if current_telemetry else (all_epochs[-1]["phase"] if all_epochs else "PHASE_1_META_EXPLORATION")
        cur_deriv = current_telemetry.efficacy_derivative if current_telemetry else (all_epochs[-1]["efficacy_derivative"] if all_epochs else 0.0)
        tokens = current_telemetry.compute_budget.token_budget if current_telemetry else (all_epochs[-1]["compute_budget"]["token_budget"] if all_epochs else 10000)
        depth = current_telemetry.compute_budget.simulation_depth if current_telemetry else (all_epochs[-1]["compute_budget"]["simulation_depth"] if all_epochs else 8)

        # Collect active and inactive axioms
        active_list = [a for a in active_axioms if a.status == AxiomStatus.ACTIVE]
        inactive_list = [a for a in active_axioms if a.status in (AxiomStatus.INACTIVE, AxiomStatus.PRUNED)]
        all_display_axioms = active_list + inactive_list
        l0_total = len([a for a in all_display_axioms if a.level == AxiomLevel.LEVEL_0_EPISTEMIC])
        l0_active = len([a for a in active_list if a.level == AxiomLevel.LEVEL_0_EPISTEMIC])
        l1_active = len([a for a in active_list if a.level == AxiomLevel.LEVEL_1_STRUCTURAL])
        l1_total = len([a for a in all_display_axioms if a.level == AxiomLevel.LEVEL_1_STRUCTURAL])
        inactive_count = len(inactive_list)

        # Lookahead radar data
        lookahead_data = (
            current_telemetry.lookahead_analysis
            if (current_telemetry and current_telemetry.lookahead_analysis)
            else (all_epochs[-1].get("lookahead_analysis") if all_epochs and "lookahead_analysis" in all_epochs[-1] else None)
        )
        lookahead_panel_html = self._render_lookahead_panel_html(lookahead_data) if lookahead_data else ""

        # Prepare JSON data for charts and client-side inspection
        epochs_json = json.dumps(all_epochs)
        active_json = json.dumps([a.to_dict() for a in active_list])
        neg_json = json.dumps([n.to_dict() for n in negative_axioms])

        is_phase_1 = cur_phase == "PHASE_1_META_EXPLORATION"
        phase_badge_color = "bg-indigo-950 text-indigo-300 border-indigo-700" if is_phase_1 else "bg-emerald-950 text-emerald-300 border-emerald-700"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Axiom Bootstrapper Telemetry & Compilation Dashboard</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-4 md:p-6 space-y-6">

  <!-- Header Banner -->
  <div class="bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-xl p-5 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
    <div>
      <div class="flex items-center gap-3">
        <span class="inline-block w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
        <h1 class="text-xl md:text-2xl font-bold tracking-tight">Axiom Bootstrapper Telemetry</h1>
        <span class="text-xs px-2.5 py-1 rounded-full font-semibold border {phase_badge_color}">
          {cur_phase}
        </span>
      </div>
      <p class="text-sm text-[var(--muted-foreground)] mt-1">Autonomous recursive systems architecture compiler · Two-tiered epistemic & structural evolution</p>
    </div>
    <div class="flex items-center gap-2 text-xs font-mono">
      <span class="px-3 py-1.5 rounded-lg border border-[var(--border)] bg-[var(--background)]">Epoch <strong class="text-emerald-400">{cur_epoch}</strong></span>
      <span class="px-3 py-1.5 rounded-lg border border-[var(--border)] bg-[var(--background)]">Global Efficacy <strong class="text-emerald-400">{cur_eff:.4f}</strong></span>
      <span class="px-3 py-1.5 rounded-lg border border-[var(--border)] bg-[var(--background)]">T(n): <strong class="text-amber-400">{tokens:,}</strong> tok</span>
    </div>
  </div>

  <!-- Key Metrics KPI Grid -->
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
      <div class="text-xs text-[var(--muted-foreground)] uppercase tracking-wider font-medium">Global Efficacy ($E$)</div>
      <div class="text-2xl font-bold mt-1 text-emerald-500">{cur_eff:.4f}</div>
      <div class="text-xs text-[var(--muted-foreground)] mt-1 flex items-center gap-1 font-mono">
        <span>dE/dt:</span>
        <span class="font-semibold text-emerald-400">{cur_deriv:+.4f}</span>
        <span class="text-[10px] text-[var(--muted-foreground)]">/ epoch</span>
      </div>
    </div>
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
      <div class="text-xs text-[var(--muted-foreground)] uppercase tracking-wider font-medium">Inverse Compute Budget</div>
      <div class="text-2xl font-bold mt-1 font-mono text-amber-400">{tokens:,}</div>
      <div class="text-xs text-[var(--muted-foreground)] mt-1">Depth limit: <strong class="text-[var(--foreground)] font-mono">{depth}</strong> steps</div>
    </div>
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
      <div class="text-xs text-[var(--muted-foreground)] uppercase tracking-wider font-medium">Active Invariants</div>
      <div class="text-2xl font-bold mt-1">{len(active_list)}</div>
      <div class="text-xs text-[var(--muted-foreground)] mt-1">
        <span class="text-indigo-400 font-semibold">{l0_active} L0</span> Meta · <span class="text-cyan-400 font-semibold">{l1_active} L1</span> Structural
      </div>
    </div>
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
      <div class="text-xs text-[var(--muted-foreground)] uppercase tracking-wider font-medium">Phase Transition Monitor</div>
      <div class="text-2xl font-bold mt-1 {'text-indigo-400' if is_phase_1 else 'text-emerald-400'} font-mono">
        {'Phase 1' if is_phase_1 else 'Phase 2'}
      </div>
      <div class="text-xs text-[var(--muted-foreground)] mt-1">
        Jettison: <span class="font-mono text-amber-300">&le; 0.002</span> (Ep &ge; 10, L0 &ge; 10)
      </div>
    </div>
  </div>

  <!-- Trajectory Chart & Dual-Tier Targets Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- SVG Trajectory Curve with Tooltip -->
    <div class="lg:col-span-2 bg-[var(--card)] border border-[var(--border)] rounded-xl p-5 shadow-sm space-y-3 relative">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="font-semibold text-base">Efficacy Trajectory & Inverse Compute Decay</h2>
          <p class="text-xs text-[var(--muted-foreground)]">Normalized Global Efficacy E(t) vs Compute Token Allocation T(n)</p>
        </div>
        <span class="text-xs font-mono px-2 py-0.5 rounded bg-[var(--background)] border border-[var(--border)] text-[var(--muted-foreground)]">T(n) &prop; 1/n</span>
      </div>

      <!-- Chart Viewport -->
      <div class="w-full h-52 bg-[var(--background)] border border-[var(--border)] rounded-lg p-2 flex items-center justify-center relative overflow-hidden" id="chart-container">
        <!-- Injected dynamic SVG -->
      </div>

      <!-- Chart Legend & Tooltip Overlay -->
      <div class="flex items-center justify-between text-xs text-[var(--muted-foreground)] px-1 pt-1 border-t border-[var(--border)]">
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-3 h-1 bg-emerald-500 rounded"></span>
            <span>Efficacy E(t) (Solid)</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-3 h-1 bg-amber-500 rounded border border-dashed"></span>
            <span>Compute Budget T(n) (Dashed)</span>
          </div>
        </div>
        <div class="text-[11px] font-mono text-[var(--muted-foreground)]">Hover nodes for telemetry drilldown</div>
      </div>

      <!-- Floating Tooltip Card -->
      <div id="chart-tooltip" class="absolute hidden pointer-events-none bg-[var(--card)] border border-[var(--border)] rounded-lg p-3 shadow-xl text-xs z-30 space-y-1.5 font-mono max-w-xs transition-opacity duration-150"></div>
    </div>

    <!-- Dual-Tier Validation Targets Panel -->
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-5 shadow-sm space-y-4 flex flex-col justify-between">
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <h2 class="font-semibold text-base">Validation Targets</h2>
          <span class="text-xs font-semibold px-2 py-0.5 rounded-full border {'bg-indigo-950 text-indigo-300 border-indigo-700' if is_phase_1 else 'bg-emerald-950 text-emerald-300 border-emerald-700'}">
            {'Phase 1 Epistemic Active' if is_phase_1 else 'Phase 2 Structural Active'}
          </span>
        </div>
        <p class="text-xs text-[var(--muted-foreground)] leading-relaxed">
          Candidates route to dedicated targets based on abstraction tier. Strict improvement (&Delta;E &gt; 0) required for commit.
        </p>

        <!-- Tier 0 Epistemic Targets -->
        <div class="space-y-2">
          <div class="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider flex items-center justify-between">
            <span>Phase 1: Epistemic Targets</span>
            <span class="text-[10px] {'text-emerald-400' if is_phase_1 else 'text-[var(--muted-foreground)]'}">{'● ACTIVE' if is_phase_1 else '○ JETTISONED'}</span>
          </div>
          <div class="space-y-1.5">
            <div class="p-2.5 rounded-lg bg-[var(--background)] border border-[var(--border)] {'opacity-100 ring-1 ring-indigo-500/30' if is_phase_1 else 'opacity-60'}">
              <div class="flex items-center justify-between text-xs font-medium">
                <span class="text-[var(--foreground)]">E₁: Search Diversity & Anti-Collapse</span>
                <span class="text-[10px] px-1.5 py-0.5 rounded font-mono bg-indigo-950 text-indigo-300 border border-indigo-800">w₁=0.35</span>
              </div>
              <p class="text-[11px] text-[var(--muted-foreground)] mt-0.5">Cross-domain topological distance & latent entropy</p>
            </div>
            <div class="p-2.5 rounded-lg bg-[var(--background)] border border-[var(--border)] {'opacity-100 ring-1 ring-indigo-500/30' if is_phase_1 else 'opacity-60'}">
              <div class="flex items-center justify-between text-xs font-medium">
                <span class="text-[var(--foreground)]">E₂: Refutation Velocity & Falsifiability</span>
                <span class="text-[10px] px-1.5 py-0.5 rounded font-mono bg-indigo-950 text-indigo-300 border border-indigo-800">w₂=0.35</span>
              </div>
              <p class="text-[11px] text-[var(--muted-foreground)] mt-0.5">Speed in rejecting vacuous or tautological claims</p>
            </div>
            <div class="p-2.5 rounded-lg bg-[var(--background)] border border-[var(--border)] {'opacity-100 ring-1 ring-indigo-500/30' if is_phase_1 else 'opacity-60'}">
              <div class="flex items-center justify-between text-xs font-medium">
                <span class="text-[var(--foreground)]">E₃: Structural Translation Yield</span>
                <span class="text-[10px] px-1.5 py-0.5 rounded font-mono bg-indigo-950 text-indigo-300 border border-indigo-800">w₃=0.30</span>
              </div>
              <p class="text-[11px] text-[var(--muted-foreground)] mt-0.5">Rate of producing valid compilable Level 1 rules</p>
            </div>
          </div>
        </div>

        <!-- Tier 1 Structural Targets (Queued) -->
        <div class="space-y-2 pt-2 border-t border-[var(--border)]">
          <div class="text-[11px] font-semibold text-cyan-400 uppercase tracking-wider flex items-center justify-between">
            <span>Phase 2: Structural Targets</span>
            <span class="text-[10px] {'text-amber-400' if is_phase_1 else 'text-emerald-400'}">{'○ QUEUED' if is_phase_1 else '● ACTIVE'}</span>
          </div>
          <div class="space-y-1.5">
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--border)] opacity-75">
              <div class="flex items-center justify-between text-xs font-medium">
                <span class="text-[var(--foreground)]">S₁: The Self-Constructor</span>
                <span class="text-[10px] font-mono text-[var(--muted-foreground)]">w₁=0.35</span>
              </div>
            </div>
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--border)] opacity-75">
              <div class="flex items-center justify-between text-xs font-medium">
                <span class="text-[var(--foreground)]">S₂: The Self-Evaluator</span>
                <span class="text-[10px] font-mono text-[var(--muted-foreground)]">w₂=0.35</span>
              </div>
            </div>
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--border)] opacity-75">
              <div class="flex items-center justify-between text-xs font-medium">
                <span class="text-[var(--foreground)]">S₃: Control Group (Byzantine Cache)</span>
                <span class="text-[10px] font-mono text-[var(--muted-foreground)]">w₃=0.30</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  {lookahead_panel_html}

  <!-- Axiom Registry & Invariant Architecture (Filterable Cards) -->
  <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-5 shadow-sm space-y-4">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
      <div>
        <h2 class="font-semibold text-base">Axiom Registry & Invariant Lineage</h2>
        <p class="text-xs text-[var(--muted-foreground)]">Persistent invariants and retained epistemic scaffolding governing recursive synthesis</p>
      </div>
      <div class="flex flex-wrap items-center gap-1.5 text-xs">
        <button onclick="filterAxioms('all')" class="px-2.5 py-1 rounded-md border border-[var(--border)] bg-[var(--background)] hover:border-emerald-500 font-medium transition-colors" id="btn-ax-all">All ({len(all_display_axioms)})</button>
        <button onclick="filterAxioms('active')" class="px-2.5 py-1 rounded-md border border-[var(--border)] bg-[var(--background)] text-emerald-400 hover:border-emerald-500 font-medium transition-colors" id="btn-ax-active">Active ({len(active_list)})</button>
        <button onclick="filterAxioms('l1')" class="px-2.5 py-1 rounded-md border border-[var(--border)] bg-[var(--background)] text-cyan-400 hover:border-cyan-500 font-medium transition-colors" id="btn-ax-l1">Level 1 Structural ({l1_total})</button>
        <button onclick="filterAxioms('l0')" class="px-2.5 py-1 rounded-md border border-[var(--border)] bg-[var(--background)] text-indigo-400 hover:border-indigo-500 font-medium transition-colors" id="btn-ax-l0">Level 0 Epistemic ({l0_total})</button>
        <button onclick="filterAxioms('inactive')" class="px-2.5 py-1 rounded-md border border-[var(--border)] bg-[var(--background)] text-amber-400 hover:border-amber-500 font-medium transition-colors" id="btn-ax-inactive">Inactive Scaffolding ({inactive_count})</button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="axioms-grid">
      {self._render_axiom_cards_html(all_display_axioms)}
    </div>
  </div>

  <!-- Historical Epochs & Tournament Telemetry (Expandable Table) -->
  <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-5 shadow-sm space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="font-semibold text-base">Epoch Trajectory & Tournament History</h2>
        <p class="text-xs text-[var(--muted-foreground)]">Head-to-head comparative evaluations, tri-fold outcomes, and HITL supervisor decisions</p>
      </div>
      <span class="text-xs font-mono px-2.5 py-1 rounded border border-[var(--border)] bg-[var(--background)] text-[var(--muted-foreground)]">
        {len(all_epochs)} epochs recorded
      </span>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left text-sm border-collapse">
        <thead>
          <tr class="border-b border-[var(--border)] text-xs text-[var(--muted-foreground)] font-medium">
            <th class="py-2.5 px-3">Epoch</th>
            <th class="py-2.5 px-3">Mode / Candidate</th>
            <th class="py-2.5 px-3">Target 1</th>
            <th class="py-2.5 px-3">Target 2</th>
            <th class="py-2.5 px-3">Target 3</th>
            <th class="py-2.5 px-3">Aggregate &Delta;E</th>
            <th class="py-2.5 px-3">Compute (Tokens)</th>
            <th class="py-2.5 px-3">Supervisor Resolution</th>
            <th class="py-2.5 px-3 text-right">Drilldown</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--border)] font-mono text-xs">
          {self._render_epoch_table_rows_html(all_epochs)}
        </tbody>
      </table>
    </div>
  </div>

  <!-- Client-side Interactive Graph & Filter Scripts -->
  <script>
    const epochs = {epochs_json};

    function filterAxioms(type) {{
      const cards = document.querySelectorAll('.axiom-card');
      cards.forEach(c => {{
        if (type === 'all') {{
          c.classList.remove('hidden');
        }} else if (type === 'active') {{
          if (c.dataset.status === 'ACTIVE') c.classList.remove('hidden');
          else c.classList.add('hidden');
        }} else if (type === 'inactive') {{
          if (c.dataset.status === 'INACTIVE') c.classList.remove('hidden');
          else c.classList.add('hidden');
        }} else if (type === 'l0') {{
          if (c.dataset.level === 'LEVEL_0_EPISTEMIC') c.classList.remove('hidden');
          else c.classList.add('hidden');
        }} else if (type === 'l1') {{
          if (c.dataset.level === 'LEVEL_1_STRUCTURAL') c.classList.remove('hidden');
          else c.classList.add('hidden');
        }}
      }});
    }}

    function toggleEpochDrawer(epochId) {{
      const drawer = document.getElementById(`epoch-drawer-${{epochId}}`);
      const icon = document.getElementById(`epoch-icon-${{epochId}}`);
      if (drawer) {{
        drawer.classList.toggle('hidden');
        if (icon) icon.classList.toggle('rotate-180');
      }}
    }}

    function renderTrajectoryChart() {{
      const container = document.getElementById('chart-container');
      const tooltip = document.getElementById('chart-tooltip');
      if (!epochs || epochs.length === 0) {{
        container.innerHTML = '<span class="text-xs text-[var(--muted-foreground)]">No historical epochs simulated yet. Awaiting Epoch 1 run.</span>';
        return;
      }}

      const w = container.clientWidth || 700;
      const h = 200;
      const padding = 45;
      const plotW = w - 2 * padding;
      const plotH = h - 2 * padding;

      // Dynamic Efficacy range
      const effValues = epochs.map(e => e.current_efficacy);
      const minEff = Math.min(...effValues) - 0.005;
      const maxEff = Math.max(...effValues) + 0.008;
      const effSpan = Math.max(0.015, maxEff - minEff);

      // Compute Tokens range (0 to 10,000)
      const maxTokens = 10000;

      // Efficacy points
      const effCoords = epochs.map((e, idx) => {{
        const x = epochs.length === 1 ? w / 2 : padding + (idx / (epochs.length - 1)) * plotW;
        const y = padding + plotH - ((e.current_efficacy - minEff) / effSpan) * plotH;
        return {{ x, y, epoch: e.epoch, eff: e.current_efficacy, tokens: (e.compute_budget ? e.compute_budget.token_budget : 10000), decision: e.decision }};
      }});

      // Compute Decay points
      const tokenCoords = epochs.map((e, idx) => {{
        const tokens = (e.compute_budget && e.compute_budget.token_budget) ? e.compute_budget.token_budget : 10000;
        const x = epochs.length === 1 ? w / 2 : padding + (idx / (epochs.length - 1)) * plotW;
        const y = padding + plotH - (tokens / maxTokens) * plotH;
        return {{ x, y }};
      }});

      const effPointsStr = effCoords.map(p => `${{p.x.toFixed(1)}},${{p.y.toFixed(1)}}`).join(' ');
      const tokenPointsStr = tokenCoords.map(p => `${{p.x.toFixed(1)}},${{p.y.toFixed(1)}}`).join(' ');

      const svg = `
        <svg viewBox="0 0 ${{w}} ${{h}}" class="w-full h-full">
          <!-- Background Grid & Axes -->
          <line x1="${{padding}}" y1="${{padding + plotH}}" x2="${{padding + plotW}}" y2="${{padding + plotH}}" stroke="currentColor" stroke-opacity="0.15" />
          <line x1="${{padding}}" y1="${{padding}}" x2="${{padding + plotW}}" y2="${{padding}}" stroke="currentColor" stroke-opacity="0.08" />
          <line x1="${{padding}}" y1="${{padding + plotH / 2}}" x2="${{padding + plotW}}" y2="${{padding + plotH / 2}}" stroke="currentColor" stroke-opacity="0.06" stroke-dasharray="2,2" />
          <line x1="${{padding}}" y1="${{padding}}" x2="${{padding}}" y2="${{padding + plotH}}" stroke="currentColor" stroke-opacity="0.15" />
          <line x1="${{padding + plotW}}" y1="${{padding}}" x2="${{padding + plotW}}" y2="${{padding + plotH}}" stroke="currentColor" stroke-opacity="0.15" />

          <!-- Compute Decay Path (Amber dashed) -->
          <polyline fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="4,4" stroke-linecap="round" points="${{tokenPointsStr}}" />

          <!-- Efficacy Trajectory Path (Emerald solid) -->
          <polyline fill="none" stroke="#10b981" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" points="${{effPointsStr}}" />

          <!-- Data Points & Labels -->
          ${{effCoords.map((p, idx) => {{
            const pTok = tokenCoords[idx];
            return `
              <!-- Compute Decay Dot -->
              <circle cx="${{pTok.x.toFixed(1)}}" cy="${{pTok.y.toFixed(1)}}" r="3.5" fill="#f59e0b" stroke="#b45309" stroke-width="1.5" />
              <text x="${{pTok.x.toFixed(1)}}" y="${{(pTok.y + 13).toFixed(1)}}" font-size="9" fill="#f59e0b" text-anchor="middle" font-family="monospace">
                T=${{p.tokens.toLocaleString()}}
              </text>

              <!-- Efficacy Interactive Dot -->
              <g class="cursor-pointer chart-node" data-epoch="${{p.epoch}}" data-eff="${{p.eff.toFixed(4)}}" data-tokens="${{p.tokens.toLocaleString()}}" data-decision="${{p.decision}}">
                <circle cx="${{p.x.toFixed(1)}}" cy="${{p.y.toFixed(1)}}" r="6" fill="#10b981" stroke="#047857" stroke-width="2" class="hover:r-8 transition-all" />
                <text x="${{p.x.toFixed(1)}}" y="${{(p.y - 10).toFixed(1)}}" font-size="10" fill="#10b981" font-weight="bold" text-anchor="middle" font-family="monospace">
                  E=${{p.eff.toFixed(4)}}
                </text>
              </g>

              <!-- Epoch Axis Label -->
              <text x="${{p.x.toFixed(1)}}" y="${{(h - 8).toFixed(1)}}" font-size="10" fill="currentColor" fill-opacity="0.6" text-anchor="middle" font-family="monospace">
                Epoch ${{p.epoch}}
              </text>
            `;
          }}).join('')}}
        </svg>
      `;
      container.innerHTML = svg;

      // Attach tooltip listeners
      const nodes = container.querySelectorAll('.chart-node');
      nodes.forEach(node => {{
        node.addEventListener('mouseenter', (ev) => {{
          const ep = node.dataset.epoch;
          const eff = node.dataset.eff;
          const tok = node.dataset.tokens;
          const dec = node.dataset.decision;
          tooltip.innerHTML = `
            <div class="text-[10px] text-[var(--muted-foreground)] uppercase">Epoch Snapshot</div>
            <div class="font-bold text-[var(--foreground)] text-sm">Epoch ${{ep}}</div>
            <div class="flex items-center justify-between gap-4 text-emerald-400">
              <span>Efficacy E:</span>
              <span class="font-bold">${{eff}}</span>
            </div>
            <div class="flex items-center justify-between gap-4 text-amber-400">
              <span>Compute Budget:</span>
              <span>${{tok}} tok</span>
            </div>
            <div class="pt-1 text-[10px] text-[var(--muted-foreground)] border-t border-[var(--border)] leading-tight">
              ${{dec}}
            </div>
          `;
          tooltip.classList.remove('hidden');
        }});

        node.addEventListener('mousemove', (ev) => {{
          const rect = container.getBoundingClientRect();
          let x = ev.clientX - rect.left + 15;
          let y = ev.clientY - rect.top - 20;
          if (x + 220 > rect.width) x -= 240;
          tooltip.style.left = `${{x}}px`;
          tooltip.style.top = `${{y}}px`;
        }});

        node.addEventListener('mouseleave', () => {{
          tooltip.classList.add('hidden');
        }});
      }});
    }}

    window.addEventListener('DOMContentLoaded', renderTrajectoryChart);
    window.addEventListener('resize', renderTrajectoryChart);
  </script>

</body>
</html>
"""

    def _render_axiom_cards_html(self, axioms: List[Axiom]) -> str:
        if not axioms:
            return '<div class="col-span-full text-xs text-[var(--muted-foreground)] p-4 rounded-lg bg-[var(--background)] border border-[var(--border)] text-center">No axioms registered yet.</div>'

        cards = []
        for ax in axioms:
            is_l0 = ax.level == AxiomLevel.LEVEL_0_EPISTEMIC
            is_inactive = ax.status in (AxiomStatus.INACTIVE, AxiomStatus.PRUNED)

            if is_inactive:
                badge_color = "bg-slate-900/90 text-amber-300 border-amber-800/60"
                status_badge = f"INACTIVE · Ep {ax.origin_epoch} Scaffold"
                card_style = "border-dashed opacity-80 hover:opacity-100 hover:border-amber-600/50"
            elif is_l0:
                badge_color = "bg-indigo-950 text-indigo-300 border-indigo-800"
                status_badge = f"ACTIVE · Epoch {ax.origin_epoch} · L0 Meta"
                card_style = "shadow-xs hover:border-indigo-500/50"
            else:
                badge_color = "bg-cyan-950 text-cyan-300 border-cyan-800"
                status_badge = f"ACTIVE · Epoch {ax.origin_epoch} · L1 Structural"
                card_style = "shadow-xs hover:border-cyan-500/50"

            cards.append(f"""
              <div class="axiom-card p-4 rounded-xl bg-[var(--background)] border border-[var(--border)] space-y-2.5 flex flex-col justify-between transition-all {card_style}" data-level="{ax.level.value}" data-status="{'INACTIVE' if is_inactive else 'ACTIVE'}">
                <div class="space-y-1.5">
                  <div class="flex items-center justify-between">
                    <span class="font-mono text-xs font-bold text-[var(--foreground)]">{ax.id}</span>
                    <span class="text-[10px] px-2 py-0.5 rounded-full border {badge_color} font-medium">{status_badge}</span>
                  </div>
                  <div class="text-xs font-bold text-[var(--foreground)]">{ax.name}</div>
                  <p class="text-[11px] text-[var(--muted-foreground)] leading-relaxed">{ax.statement}</p>
                </div>
                
                <div class="space-y-1.5 pt-2 border-t border-[var(--border)]">
                  <div class="text-[10px] font-mono text-[var(--muted-foreground)] bg-[var(--card)] px-2.5 py-1.5 rounded border border-[var(--border)] overflow-x-auto">
                    <span class="text-indigo-400 font-semibold">&fnof;:</span> {ax.formal_expression}
                  </div>
                  <div class="text-[10px] font-mono text-emerald-400 bg-[var(--card)] px-2.5 py-1.5 rounded border border-[var(--border)] leading-snug">
                    <span class="text-emerald-500 font-semibold">&bull; Rule:</span> {ax.operational_rule}
                  </div>
                </div>
              </div>
            """)
        return "".join(cards)

    def _render_lookahead_panel_html(self, la: Optional[Dict[str, Any]]) -> str:
        if not la:
            return ""

        jb = la.get("jettison_branch", {})
        rb = la.get("retain_branch", {})
        rec = la.get("recommendation", "INCONCLUSIVE")
        conf = int(la.get("confidence_score", 0.5) * 100)
        net_diff = la.get("net_lookahead_differential", 0.0)
        tok_div = la.get("compute_dividend_tokens", 0)
        horizon = la.get("lookahead_horizon", 2)

        rec_style = (
            "bg-emerald-950 text-emerald-300 border-emerald-700"
            if rec == "RECOMMEND_JETTISON"
            else ("bg-amber-950 text-amber-300 border-amber-700" if rec == "RECOMMEND_RETAIN" else "bg-slate-900 text-slate-300 border-slate-700")
        )

        return f"""
  <!-- Axiom Lookahead: Jettison Speculative Radar Panel -->
  <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-5 shadow-sm space-y-4">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
      <div class="flex items-center gap-2">
        <span class="inline-block w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse"></span>
        <h2 class="font-semibold text-base">Axiom Lookahead · Jettison Speculative Radar</h2>
        <span class="text-xs px-2.5 py-0.5 rounded-full font-mono bg-cyan-950 text-cyan-300 border border-cyan-800">
          Horizon: H={horizon} Epochs Forward
        </span>
      </div>
      <div class="flex items-center gap-2 text-xs">
        <span class="font-semibold px-2.5 py-1 rounded-full border {rec_style}">
          {rec} (Confidence: {conf}%)
        </span>
        <span class="font-mono px-2.5 py-1 rounded border border-[var(--border)] bg-[var(--background)] text-emerald-400 font-bold">
          &Lambda;<sub>H</sub>: {net_diff:+.4f}
        </span>
      </div>
    </div>

    <!-- Dual Branch Comparison Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
      <!-- Branch A: Speculative Jettison -->
      <div class="p-4 rounded-xl bg-[var(--background)] border border-emerald-500/40 space-y-3">
        <div class="flex items-center justify-between border-b border-[var(--border)] pb-2">
          <span class="font-bold text-sm text-emerald-400">Branch A: Speculative Jettison</span>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
            +{tok_div:,} tok dividend
          </span>
        </div>
        <div class="grid grid-cols-3 gap-2 font-mono text-center">
          <div class="p-2 rounded bg-[var(--card)] border border-[var(--border)]">
            <div class="text-[9px] text-[var(--muted-foreground)] uppercase">Active n</div>
            <div class="text-sm font-bold text-[var(--foreground)] mt-0.5">{jb.get('active_axiom_count', 0)}</div>
          </div>
          <div class="p-2 rounded bg-[var(--card)] border border-[var(--border)]">
            <div class="text-[9px] text-[var(--muted-foreground)] uppercase">Token Budget</div>
            <div class="text-sm font-bold text-amber-400 mt-0.5">{jb.get('tokens', 0):,}</div>
          </div>
          <div class="p-2 rounded bg-[var(--card)] border border-[var(--border)]">
            <div class="text-[9px] text-[var(--muted-foreground)] uppercase">Sim Depth</div>
            <div class="text-sm font-bold text-cyan-400 mt-0.5">{jb.get('depth', 0)} steps</div>
          </div>
        </div>
        <div class="p-2 rounded bg-[var(--card)] border border-[var(--border)] flex items-center justify-between">
          <span class="text-[11px] text-[var(--muted-foreground)]">Projected Cumulative Yield:</span>
          <span class="font-mono text-sm font-bold text-emerald-400">{jb.get('projected_cumulative_delta', 0.0):+.4f}</span>
        </div>
        <p class="text-[11px] text-[var(--muted-foreground)] leading-relaxed">{jb.get('rationale', '')}</p>
      </div>

      <!-- Branch B: Retain Epistemic Scaffolding -->
      <div class="p-4 rounded-xl bg-[var(--background)] border border-indigo-500/40 space-y-3">
        <div class="flex items-center justify-between border-b border-[var(--border)] pb-2">
          <span class="font-bold text-sm text-indigo-400">Branch B: Retain Epistemic Scaffolding</span>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
            Epistemic Rules Active
          </span>
        </div>
        <div class="grid grid-cols-3 gap-2 font-mono text-center">
          <div class="p-2 rounded bg-[var(--card)] border border-[var(--border)]">
            <div class="text-[9px] text-[var(--muted-foreground)] uppercase">Active n</div>
            <div class="text-sm font-bold text-[var(--foreground)] mt-0.5">{rb.get('active_axiom_count', 0)}</div>
          </div>
          <div class="p-2 rounded bg-[var(--card)] border border-[var(--border)]">
            <div class="text-[9px] text-[var(--muted-foreground)] uppercase">Token Budget</div>
            <div class="text-sm font-bold text-amber-400 mt-0.5">{rb.get('tokens', 0):,}</div>
          </div>
          <div class="p-2 rounded bg-[var(--card)] border border-[var(--border)]">
            <div class="text-[9px] text-[var(--muted-foreground)] uppercase">Sim Depth</div>
            <div class="text-sm font-bold text-cyan-400 mt-0.5">{rb.get('depth', 0)} steps</div>
          </div>
        </div>
        <div class="p-2 rounded bg-[var(--card)] border border-[var(--border)] flex items-center justify-between">
          <span class="text-[11px] text-[var(--muted-foreground)]">Projected Cumulative Yield:</span>
          <span class="font-mono text-sm font-bold text-indigo-400">{rb.get('projected_cumulative_delta', 0.0):+.4f}</span>
        </div>
        <p class="text-[11px] text-[var(--muted-foreground)] leading-relaxed">{rb.get('rationale', '')}</p>
      </div>
    </div>
  </div>
"""

    def _render_epoch_table_rows_html(self, records: List[Dict[str, Any]]) -> str:
        if not records:
            return '<tr><td colspan="9" class="py-4 text-center text-xs text-[var(--muted-foreground)]">No epochs recorded yet</td></tr>'

        rows = []
        for r in records:
            ep = r.get("epoch", 0)
            cand = r.get("candidate_axiom") or {}
            cand_id = cand.get("id", "-")
            cand_name = cand.get("name", "")
            m = r.get("tri_fold_metrics") or {}
            d1 = f"{m.get('delta_e1', 0.0):+.4f}" if "delta_e1" in m else "-"
            d2 = f"{m.get('delta_e2', 0.0):+.4f}" if "delta_e2" in m else "-"
            d3 = f"{m.get('delta_e3', 0.0):+.4f}" if "delta_e3" in m else "-"
            agg = f"{m.get('aggregate_delta_e', 0.0):+.4f}" if "aggregate_delta_e" in m else "-"
            budget = r.get("compute_budget", {})
            tokens = budget.get("token_budget", 0)
            decision = r.get("decision", "-")

            # Check if tournament mode was active
            comp = r.get("comparative_summary")
            user_cand = r.get("user_candidate") or {}
            user_m = r.get("user_metrics") or {}

            cand_display = f"[{cand_id}] {cand_name[:24]}..." if cand_id != "-" else "Seed Baseline"
            if comp:
                cand_display += " <span class='text-amber-400 font-semibold'>[⚔️ Tourney]</span>"

            rows.append(f"""
              <tr class="hover:bg-[var(--background)] transition-colors cursor-pointer" onclick="toggleEpochDrawer({ep})">
                <td class="py-2.5 px-3 font-bold text-[var(--foreground)]">{ep}</td>
                <td class="py-2.5 px-3 font-sans">{cand_display}</td>
                <td class="py-2.5 px-3 text-emerald-400">{d1}</td>
                <td class="py-2.5 px-3 text-cyan-400">{d2}</td>
                <td class="py-2.5 px-3 text-amber-400">{d3}</td>
                <td class="py-2.5 px-3 font-bold text-emerald-400">{agg}</td>
                <td class="py-2.5 px-3 text-[var(--muted-foreground)]">{tokens:,}</td>
                <td class="py-2.5 px-3 font-sans text-xs">{decision}</td>
                <td class="py-2.5 px-3 text-right">
                  <span class="inline-block transition-transform duration-200 text-[var(--muted-foreground)]" id="epoch-icon-{ep}">▼</span>
                </td>
              </tr>
            """)

            # Expandable Drawer Row
            if comp or cand_id != "-":
                tournament_html = ""
                leaderboard = r.get("tournament_leaderboard")
                if leaderboard and len(leaderboard) > 1:
                    leaderboard_rows = []
                    for idx, item in enumerate(leaderboard, 1):
                        is_winner = idx == 1 and item.get("is_strictly_improving", False)
                        status_badge = "<span class='px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 font-bold border border-emerald-800'>🏆 WINNER</span>" if is_winner else "<span class='px-1.5 py-0.5 rounded bg-neutral-900 text-[var(--muted-foreground)]'>Outperformed</span>"
                        leaderboard_rows.append(f"""
                          <tr class="border-b border-[var(--border)] {'bg-emerald-950/20' if is_winner else ''}">
                            <td class="py-1.5 px-2 font-bold">{idx}</td>
                            <td class="py-1.5 px-2 font-semibold text-[var(--foreground)]">[{item.get('id')}] {item.get('name')}</td>
                            <td class="py-1.5 px-2 text-[var(--muted-foreground)]">{item.get('domain', '-')}</td>
                            <td class="py-1.5 px-2 text-emerald-400 font-mono">{item.get('delta_e1', 0):+.4f}</td>
                            <td class="py-1.5 px-2 text-cyan-400 font-mono">{item.get('delta_e2', 0):+.4f}</td>
                            <td class="py-1.5 px-2 text-amber-400 font-mono">{item.get('delta_e3', 0):+.4f}</td>
                            <td class="py-1.5 px-2 font-bold text-emerald-400 font-mono">{item.get('aggregate_delta_e', 0):+.4f}</td>
                            <td class="py-1.5 px-2">{status_badge}</td>
                          </tr>
                        """)

                    tournament_html = f"""
                      <div class="p-3 rounded-lg bg-[var(--card)] border border-amber-500/30 space-y-2.5">
                        <div class="flex items-center justify-between text-xs">
                          <span class="font-bold text-amber-400">⚔️ Autonomous Multi-Candidate Tournament ({len(leaderboard)} candidates evaluated)</span>
                          <span class="font-mono text-[11px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                            Winner: [{leaderboard[0].get('id')}] (&Delta;E = {leaderboard[0].get('aggregate_delta_e', 0):+.4f})
                          </span>
                        </div>
                        <div class="overflow-x-auto">
                          <table class="w-full text-left text-xs border-collapse">
                            <thead>
                              <tr class="border-b border-[var(--border)] text-[10px] text-[var(--muted-foreground)] font-mono">
                                <th class="py-1 px-2">Rank</th>
                                <th class="py-1 px-2">Candidate Axiom</th>
                                <th class="py-1 px-2">Exogenous Domain</th>
                                <th class="py-1 px-2">T1</th>
                                <th class="py-1 px-2">T2</th>
                                <th class="py-1 px-2">T3</th>
                                <th class="py-1 px-2">Aggregate &Delta;E</th>
                                <th class="py-1 px-2">Outcome</th>
                              </tr>
                            </thead>
                            <tbody class="divide-y divide-[var(--border)] font-mono text-xs">
                              {''.join(leaderboard_rows)}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    """

                    arch_cards = []
                    for item in leaderboard:
                        prof = item.get("system_profile") or {}
                        archetype = prof.get("archetype", f"System Archetype ({item.get('id')})")
                        diag = prof.get("topology_diagram", "")
                        subs = prof.get("subsystems") or {}
                        behaviors = prof.get("target_behaviors") or {}
                        agg_val = float(item.get("aggregate_delta_e") or 0.0)

                        sub_items = []
                        for s_name, s_info in subs.items():
                            if isinstance(s_info, dict):
                                sub_items.append(f"<li class='text-[10px]'><strong class='text-[var(--foreground)]'>{s_name}</strong>: {s_info.get('role', '')} (<span class='text-emerald-400 font-mono'>{s_info.get('invariant_rule', '')}</span>)</li>")
                            else:
                                sub_items.append(f"<li class='text-[10px]'><strong class='text-[var(--foreground)]'>{s_name}</strong>: {s_info}</li>")
                        sub_html = f"<ul class='list-disc list-inside space-y-0.5 pt-1 text-[var(--muted-foreground)]'>{''.join(sub_items[:3])}</ul>" if sub_items else ""

                        diag_html = f"<pre class='p-2 rounded bg-[var(--background)] border border-[var(--border)] font-mono text-[9px] text-emerald-400 overflow-x-auto whitespace-pre leading-tight mt-1'>{diag.strip()}</pre>" if diag else ""

                        behav_items = []
                        for b_k, b_v in behaviors.items():
                            b_label = b_k.replace("target_", "").upper()
                            behav_items.append(f"<div class='text-[10px]'><span class='font-mono font-semibold text-cyan-400'>{b_label}:</span> {b_v}</div>")
                        behav_html = f"<div class='space-y-0.5 pt-1 border-t border-[var(--border)] text-[var(--muted-foreground)]'>{''.join(behav_items[:3])}</div>" if behav_items else ""

                        arch_cards.append(f"""
                          <div class="p-3 rounded-lg bg-[var(--background)] border border-[var(--border)] space-y-2 text-xs">
                            <div class="flex items-center justify-between">
                              <span class="font-mono font-bold text-amber-400">[{item.get('id')}] {item.get('name')}</span>
                              <span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 font-mono font-bold">&Delta;E = {agg_val:+.4f}</span>
                            </div>
                            <div class="text-[11px] text-[var(--muted-foreground)]"><strong class="text-indigo-400">Archetype:</strong> {archetype}</div>
                            {diag_html}
                            <div class="space-y-1">
                              <div class="font-semibold text-[11px] text-[var(--foreground)]">Synthesized Subsystems:</div>
                              {sub_html}
                            </div>
                            {behav_html}
                          </div>
                        """)

                    cols_count = min(len(leaderboard), 3)
                    tournament_html += f"""
                      <div class="mt-3 pt-3 border-t border-[var(--border)] space-y-2.5">
                        <div class="flex items-center justify-between text-xs">
                          <span class="font-bold text-[var(--foreground)]">📐 Evaluated Candidate System Architectures & Topologies</span>
                          <span class="text-[10px] text-[var(--muted-foreground)] font-mono">{len(leaderboard)} architectures profiled</span>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-{cols_count} gap-3">
                          {''.join(arch_cards)}
                        </div>
                      </div>
                    """
                elif comp:
                    tournament_html = f"""
                      <div class="p-3 rounded-lg bg-[var(--card)] border border-amber-500/30 space-y-2">
                        <div class="flex items-center justify-between text-xs">
                          <span class="font-bold text-amber-400">⚔️ Head-to-Head Comparative Tournament</span>
                          <span class="font-mono text-[11px] px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
                            Winner: {'User Seed' if comp.get('user_won') else 'LLM Candidate'} (&Delta;&Delta;E = {comp.get('delta_diff'):+.4f})
                          </span>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                          <!-- LLM Side -->
                          <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--border)] space-y-1">
                            <div class="font-semibold text-cyan-400">LLM Hypothesis: [{cand_id}] {cand_name}</div>
                            <div class="text-[11px] text-[var(--muted-foreground)]">{cand.get('statement', '')}</div>
                            <div class="font-mono text-[10px] text-emerald-400 pt-1">
                              &Delta;E₁={m.get('delta_e1', 0):+.4f} | &Delta;E₂={m.get('delta_e2', 0):+.4f} | &Delta;E₃={m.get('delta_e3', 0):+.4f} &rarr; <strong>&Delta;E = {m.get('aggregate_delta_e', 0):+.4f}</strong>
                            </div>
                          </div>
                          <!-- User Seed Side -->
                          <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--border)] space-y-1">
                            <div class="font-semibold text-indigo-400">Human Seed: [{user_cand.get('id', '')}] {user_cand.get('name', '')}</div>
                            <div class="text-[11px] text-[var(--muted-foreground)]">{user_cand.get('statement', '')}</div>
                            <div class="font-mono text-[10px] text-emerald-400 pt-1">
                              &Delta;E₁={user_m.get('delta_e1', 0):+.4f} | &Delta;E₂={user_m.get('delta_e2', 0):+.4f} | &Delta;E₃={user_m.get('delta_e3', 0):+.4f} &rarr; <strong>&Delta;E = {user_m.get('aggregate_delta_e', 0):+.4f}</strong>
                            </div>
                          </div>
                        </div>
                      </div>
                    """
                else:
                    tournament_html = f"""
                      <div class="p-3 rounded-lg bg-[var(--card)] border border-[var(--border)] text-xs space-y-1">
                        <div class="font-semibold text-[var(--foreground)]">Candidate: [{cand_id}] {cand_name}</div>
                        <div class="text-[11px] text-[var(--muted-foreground)]">{cand.get('statement', '')}</div>
                        <div class="font-mono text-[10px] text-emerald-400">Rule: {cand.get('operational_rule', '')}</div>
                      </div>
                    """

                rows.append(f"""
                  <tr class="hidden bg-[var(--background)]" id="epoch-drawer-{ep}">
                    <td colspan="9" class="p-3 border-b border-[var(--border)] font-sans">
                      {tournament_html}
                    </td>
                  </tr>
                """)
            else:
                rows.append(f"""
                  <tr class="hidden bg-[var(--background)]" id="epoch-drawer-{ep}">
                    <td colspan="9" class="p-3 border-b border-[var(--border)] font-sans text-xs text-[var(--muted-foreground)]">
                      Epoch 0 baseline: System initialized from bootstrap seeds L0-001 (Compositionality) and L0-002 (Information Gradient).
                    </td>
                  </tr>
                """)

        return "".join(rows)
