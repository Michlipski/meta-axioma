"""Recursion Tree Visualizer and Boundary Opinion Telemetry for System G2b."""

import datetime
import json
from pathlib import Path
from typing import List, Optional

from g2b_compiler.recursion.models import BoundaryOpinion, RecursionNode


WORKER_DISPLAY_NAMES = {
    "orchestrator": "Orchestrator",
    "research": "ResearchWorker",
    "synthesis": "SynthesisWorker",
    "anti_mock_linter": "AntiMockLinter",
    "model_checker": "ModelChecker",
    "structural_regulator": "StructuralRegulator",
    "usability_auditor": "UsabilityAuditor",
    "adversarial_falsifier": "AdversarialFalsifier",
    "substrate_runner": "SubstrateRunner",
    "terminal_sink": "TerminalSink",
}


class RecursionTreeVisualizer:
    """Emits live Mermaid DAGs and Markdown audit logs of the recursive orchestration execution tree."""

    def __init__(self, run_id: str, telemetry_dir: Optional[Path] = None):
        self.run_id = run_id
        repo_root = Path(__file__).resolve().parents[5]
        self.central_telemetry_dir = repo_root / "trace" / "telemetry"
        self.central_telemetry_dir.mkdir(parents=True, exist_ok=True)
        self.central_opinions_log = self.central_telemetry_dir / "recursion_depth_opinions.jsonl"
        self.central_decisions_log = self.central_telemetry_dir / "orchestration_decisions.jsonl"
        self.central_proposals_log = self.central_telemetry_dir / "project_proposals.jsonl"

        if telemetry_dir is None:
            self.telemetry_dir = self.central_telemetry_dir
            self.opinions_log = self.central_opinions_log
            self.decisions_log = self.central_decisions_log
            self.proposals_log = self.central_proposals_log
        else:
            self.telemetry_dir = Path(telemetry_dir)
            self.telemetry_dir.mkdir(parents=True, exist_ok=True)
            self.opinions_log = self.telemetry_dir / "recursion_depth_opinions.jsonl"
            self.decisions_log = self.telemetry_dir / "orchestration_decisions.jsonl"
            self.proposals_log = self.telemetry_dir / "project_proposals.jsonl"

    def record_project_proposals(self, dossier: Any):
        """Appends project proposal options to the telemetry log."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        for p in dossier.proposals:
            entry = {
                "run_id": self.run_id,
                "timestamp": timestamp,
                "app_id": dossier.app_id,
                "elevator_pitch": dossier.elevator_pitch,
                "tier_id": p.tier_id,
                "title": p.title,
                "raw_estimated_tokens": p.raw_estimated_tokens,
                "bounded_token_budget": p.bounded_token_budget,
                "protected_capital": p.protected_capital,
                "exploratory_capital": p.exploratory_capital,
                "selected": (p.tier_id == dossier.selected_proposal_id),
                "rationale": p.rationale,
            }
            with open(self.proposals_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            if self.proposals_log.resolve() != self.central_proposals_log.resolve():
                with open(self.central_proposals_log, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry) + "\n")

    def record_selection_decisions(self, parent_node: RecursionNode, decisions: List[Any]):
        """Records orchestrator subagent selection and token allotment rationale to telemetry."""
        parent_node.selection_decisions = decisions
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        for d in decisions:
            entry = {
                "run_id": self.run_id,
                "timestamp": timestamp,
                "parent_id": parent_node.node_id,
                "parent_name": parent_node.name,
                "parent_worker": parent_node.worker_type.value,
                "candidate_worker": d.worker_type.value if hasattr(d.worker_type, "value") else str(d.worker_type),
                "chosen": d.chosen,
                "subgoal": d.subgoal,
                "allotted_tokens": d.allotted_tokens,
                "used_tokens": d.used_tokens,
                "rationale": d.rationale
            }
            with open(self.decisions_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

            if self.decisions_log.resolve() != self.central_decisions_log.resolve():
                with open(self.central_decisions_log, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry) + "\n")

    def record_boundary_opinion(self, node: RecursionNode, opinion: BoundaryOpinion):
        """Appends an LLM depth-boundary reflection probe to the telemetry log."""
        node.boundary_opinion = opinion
        entry = {
            "run_id": self.run_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "node_id": node.node_id,
            "worker_type": node.worker_type.value,
            "depth": node.depth,
            "effective_depth": node.effective_depth,
            "wants_depth_extension": opinion.wants_depth_extension,
            "confidence": opinion.confidence,
            "rationale": opinion.rationale,
            "estimated_token_cost": opinion.estimated_token_cost,
            "subgoal": opinion.subgoal
        }
        with open(self.opinions_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        if self.opinions_log.resolve() != self.central_opinions_log.resolve():
            with open(self.central_opinions_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

    def generate_mermaid_dag(self, root: RecursionNode) -> str:
        """Generates Mermaid flowchart notation for the recursion tree."""
        lines = ["flowchart TD"]

        def traverse(node: RecursionNode):
            status_symbol = "✓" if node.status == "SUCCESS" else ("✕" if node.status == "FAILED" else ("⚡" if node.status == "REPAIRED" else "⏳"))
            w_val = node.worker_type.value if hasattr(node.worker_type, "value") else str(node.worker_type)
            display_worker = WORKER_DISPLAY_NAMES.get(w_val, w_val)
            subgoal_str = f"<br/><i>{node.subgoal}</i>" if node.subgoal else (f"<br/><i>{node.name}</i>" if node.name != display_worker else "")
            
            # Format token allotment vs usage
            if node.children:
                tok_str = f"Env: {node.token_cost:,} (Self: {node.self_allotted:,}) | Used: {node.tokens_used:,} tok"
            elif node.tokens_used > 0:
                tok_str = f"{node.token_cost:,}/{node.tokens_used:,} tok"
            else:
                tok_str = f"{node.token_cost:,} tok"
                
            label = f"{display_worker}{subgoal_str}<br/>(d={node.depth} eff={node.effective_depth:.1f} | {tok_str}) [{status_symbol}]"
            # Sanitize for mermaid
            safe_label = label.replace('"', "'")
            lines.append(f'    {node.node_id}["{safe_label}"]')
            for child in node.children:
                lines.append(f"    {node.node_id} --> {child.node_id}")
                traverse(child)

        traverse(root)
        return "\n".join(lines)

    def emit_tree_report(self, root: RecursionNode, target_path: Path, cost_summary: Optional[dict] = None):
        """Writes recursion_tree.md report with Mermaid diagram, boundary telemetry, and decision audit tables."""
        dag = self.generate_mermaid_dag(root)
        total_allotted = cost_summary["total_allotted"] if (cost_summary and "total_allotted" in cost_summary) else self._sum_allotted_tokens(root)
        total_used = cost_summary["total_used"] if (cost_summary and "total_used" in cost_summary) else self._sum_used_tokens(root)
        max_depth = self._max_depth(root)
        utilization = (total_used / total_allotted * 100.0) if total_allotted > 0 else 0.0

        budget_line = ""
        if cost_summary and "total_budget" in cost_summary:
            budget_line = (
                f"> **Global Budget:** {cost_summary['total_budget']:,} tokens "
                f"(Protected: {cost_summary['protected_reserved']:,} | Exploratory: {cost_summary['exploratory_reserved']:,})  \n"
            )

        content = f"""# System G2b Orchestration Recursion Tree

> **Run ID:** `{self.run_id}`  
> **Timestamp:** {datetime.datetime.now(datetime.timezone.utc).isoformat()}  
> **Max Depth Traversed:** {max_depth}  
{budget_line}> **Total Tokens Allotted:** {total_allotted:,} tokens  
> **Total Tokens Used:** {total_used:,} tokens ({utilization:.1f}% efficiency)  

---

## 1. Execution Tree DAG

```mermaid
{dag}
```

---

## 2. Boundary Depth Opinions Recorded

"""
        opinions = self._collect_opinions(root)
        if not opinions:
            content += "_No boundary depth opinions recorded for this run (branches concluded within depth bounds)._\n"
        else:
            content += "| Node | Worker | Wants Depth 4? | Confidence | Rationale | Est. Cost |\n"
            content += "| :--- | :--- | :---: | :---: | :--- | :---: |\n"
            for n, op in opinions:
                wants = "YES" if op.wants_depth_extension else "NO"
                op_w_val = op.worker_type.value if hasattr(op.worker_type, "value") else str(op.worker_type)
                w_name = WORKER_DISPLAY_NAMES.get(op_w_val, op_w_val)
                node_label = f"{n.name} ({n.subgoal})" if n.subgoal else n.name
                content += f"| `{node_label}` | `{w_name}` | **{wants}** | {op.confidence:.2f} | {op.rationale} | {op.estimated_token_cost} tok |\n"

        content += "\n---\n\n## 3. Orchestrator Subagent Selection & Token Allotment Rationale\n\n"
        decisions_by_node = self._collect_all_decisions(root)
        if not decisions_by_node:
            content += "_No explicit selection decision logs recorded._\n"
        else:
            content += "| Parent Node | Evaluated Subagent | Chosen? | Allotment | Tokens Used | Efficiency | Rationale |\n"
            content += "| :--- | :--- | :---: | :---: | :---: | :---: | :--- |\n"
            for parent, d_list in decisions_by_node:
                p_label = f"{parent.name} (`{parent.subgoal or parent.node_id}`)"
                for d in d_list:
                    cand_val = d.worker_type.value if hasattr(d.worker_type, "value") else str(d.worker_type)
                    cand_name = WORKER_DISPLAY_NAMES.get(cand_val, cand_val)
                    if d.chosen:
                        chosen_badge = "**YES**"
                        allot_str = f"{d.allotted_tokens:,} tok"
                        used_str = f"{d.used_tokens:,} tok" if d.used_tokens > 0 else f"{d.allotted_tokens:,} tok"
                        eff = (d.used_tokens / d.allotted_tokens * 100.0) if d.allotted_tokens > 0 else 100.0
                        eff_str = f"{eff:.1f}%"
                    else:
                        chosen_badge = "NO"
                        allot_str = "-"
                        used_str = "-"
                        eff_str = "-"
                    content += f"| `{p_label}` | `{cand_name}` | {chosen_badge} | {allot_str} | {used_str} | {eff_str} | {d.rationale} |\n"

        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")

    def emit_proposals_report(self, dossier: Any, target_path: Path):
        """Writes project_proposals.md report with comparison matrix and deliverables."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        content = f"""# System G2b Project Proposal Dossier

> **App ID:** `{dossier.app_id}`  
> **Run ID:** `{self.run_id}`  
> **Timestamp:** {timestamp}  
> **Budget Range Bound:** Min {dossier.min_budget_bound:,} tokens $\\longleftrightarrow$ Safety Max {dossier.max_safety_budget_bound:,} tokens  
> **Selected Proposal Tier:** `{dossier.selected_proposal_id}`  

---

## 1. Problem Space & Domain Research Baselines

> **Elevator Pitch:**  
> *"{dossier.elevator_pitch}"*  

**Domain Research Grounding:**  
{dossier.research_summary}

---

## 2. Dynamic Project Proposals Matrix

| Proposal Tier | Bounded Budget | Protected (40%) | Exploratory (60%) | Scope Summary | Statechart Complexity | Status |
| :--- | :---: | :---: | :---: | :--- | :--- | :---: |
"""
        for p in dossier.proposals:
            sel_badge = "**SELECTED**" if p.tier_id == dossier.selected_proposal_id else "AVAILABLE"
            feats = f"{len(p.included_features)} features ({', '.join(p.included_features[:2])}...)"
            content += f"| **{p.title}** (`{p.tier_id}`) | **{p.bounded_token_budget:,} tok** | {p.protected_capital:,} tok | {p.exploratory_capital:,} tok | {feats} | {p.statechart_complexity} | {sel_badge} |\n"

        content += "\n---\n\n## 3. Detailed Scope Tiers & Engineering Deliverables\n\n"
        for p in dossier.proposals:
            status_header = " ⭐ ACTIVE SELECTION" if p.tier_id == dossier.selected_proposal_id else ""
            content += f"### Tier: {p.title} (`{p.tier_id}`){status_header}\n\n"
            content += f"- **Target Persona Fit:** {p.target_persona_fit}\n"
            content += f"- **Total Bounded Budget:** **{p.bounded_token_budget:,} tokens** (Raw Estimate: {p.raw_estimated_tokens:,} tokens)\n"
            content += f"  - **Protected Capital (40% Verification Sinks):** {p.protected_capital:,} tokens\n"
            content += f"  - **Exploratory Capital (60% Synthesis Leases):** {p.exploratory_capital:,} tokens\n"
            if hasattr(p, "workload_breakdown") and p.workload_breakdown:
                wb = p.workload_breakdown
                content += "  - **Task-to-Token Workload Allocation:**\n"
                if "research_and_grounding" in wb:
                    content += f"    - *Research & Domain Grounding:* {wb['research_and_grounding']:,} tokens\n"
                if "architecture_and_ir" in wb:
                    content += f"    - *Architecture & Statechart IR:* {wb['architecture_and_ir']:,} tokens\n"
                if "code_and_ast_emission" in wb:
                    content += f"    - *Code & UI AST Emission:* {wb['code_and_ast_emission']:,} tokens\n"
                if "model_checking_reachability" in wb:
                    content += f"    - *Model Checking & Reachability (Protected):* {wb['model_checking_reachability']:,} tokens\n"
                if "falsification_and_substrate" in wb:
                    content += f"    - *Falsification & Substrate Tests (Protected):* {wb['falsification_and_substrate']:,} tokens\n"
            content += f"- **Statechart Complexity:** {p.statechart_complexity}\n"
            content += f"- **Verification Depth:** {p.verification_depth}\n"
            content += f"- **Included Features:** {', '.join(p.included_features)}\n"
            if p.deferred_features:
                content += f"- **Deferred / Cut Features:** {', '.join(p.deferred_features)}\n"
            content += f"- **Engineering Rationale:** {p.rationale}\n"
            if hasattr(p, "token_justification") and p.token_justification:
                content += f"- **Why This Token Budget Fits the Workload:** {p.token_justification}\n"
            content += "\n"

        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")

    def emit_html_dashboard(
        self,
        root: RecursionNode,
        target_path: Path,
        cost_summary: Optional[dict] = None,
        proposal_dossier: Optional[Any] = None,
    ):
        """Emits an interactive, visual HTML dashboard for telemetry inspection."""
        dag = self.generate_mermaid_dag(root)
        total_allotted = cost_summary["total_allotted"] if (cost_summary and "total_allotted" in cost_summary) else self._sum_allotted_tokens(root)
        total_used = cost_summary["total_used"] if (cost_summary and "total_used" in cost_summary) else self._sum_used_tokens(root)
        max_depth = self._max_depth(root)
        utilization = (total_used / total_allotted * 100.0) if total_allotted > 0 else 0.0

        decisions_by_node = self._collect_all_decisions(root)
        opinions = self._collect_opinions(root)

        proposals_html = ""
        if proposal_dossier and hasattr(proposal_dossier, "proposals"):
            table_rows_html = ""
            cards_html = ""
            for p in proposal_dossier.proposals:
                is_sel = (p.tier_id == proposal_dossier.selected_proposal_id)
                badge_class = "badge-chosen" if is_sel else "badge-rejected"
                badge_lbl = "ACTIVE SELECTION" if is_sel else "AVAILABLE TIER"
                row_class = "row-chosen" if is_sel else "row-skipped"
                scope_items = "".join(f"<div style='margin-bottom: 2px;'>• {f}</div>" for f in p.included_features)

                table_rows_html += f"""
                <tr class="{row_class}">
                    <td class="col-fit">
                        <strong style="color: {'var(--primary)' if is_sel else 'var(--text)'}; font-size: 13px;">{p.title}</strong>
                        <div style="font-size: 11px; color: var(--muted); font-family: monospace;">{p.tier_id}</div>
                    </td>
                    <td class="col-fit col-center"><span class="badge {badge_class}">{badge_lbl}</span></td>
                    <td class="col-fit col-num"><strong style="font-size: 14px;">{p.bounded_token_budget:,}</strong> <span style="font-size: 11px; color: var(--muted);">tok</span></td>
                    <td class="col-fit col-num" style="color: var(--primary); font-weight: 600;">{p.protected_capital:,} tok</td>
                    <td class="col-fit col-num" style="color: #c084fc; font-weight: 600;">{p.exploratory_capital:,} tok</td>
                    <td class="col-fit"><span style="font-size: 12px; color: var(--muted);">{p.statechart_complexity}</span></td>
                    <td class="col-auto"><div style="font-size: 12px; line-height: 1.4; color: var(--text);"><em>{p.target_persona_fit}</em></div></td>
                    <td class="col-auto"><div style="font-size: 11px; line-height: 1.35; color: var(--muted);">{scope_items}</div></td>
                    <td class="col-auto">
                        <div style="font-size: 12px; line-height: 1.4; color: var(--text); margin-bottom: 4px;">{p.rationale}</div>
                        {f"<div style='font-size: 11px; line-height: 1.35; color: var(--primary);'><strong>Budget Justification:</strong> {p.token_justification}</div>" if (hasattr(p, 'token_justification') and p.token_justification) else ""}
                    </td>
                </tr>
                """

                badge_style = "background: rgba(52, 211, 153, 0.2); color: var(--success); border: 1px solid var(--success);" if is_sel else "background: rgba(148, 163, 184, 0.1); color: var(--muted); border: 1px solid var(--border);"
                card_border = "border: 2px solid var(--success);" if is_sel else "border: 1px solid var(--border);"
                
                workload_html = ""
                if hasattr(p, "workload_breakdown") and p.workload_breakdown:
                    wb = p.workload_breakdown
                    workload_html = f"""
                    <div style="font-size: 11px; background: rgba(15, 23, 42, 0.5); border: 1px solid var(--border); border-radius: 4px; padding: 6px 8px; margin-bottom: 8px;">
                        <div style="color: var(--primary); font-weight: 600; margin-bottom: 2px;">Task-to-Token Allocation:</div>
                        <div style="font-family: monospace; font-size: 10px; color: var(--muted); line-height: 1.4;">
                            • Research: {wb.get('research_and_grounding', 0):,} tok<br>
                            • IR & Contracts: {wb.get('architecture_and_ir', 0):,} tok<br>
                            • Code Emission: {wb.get('code_and_ast_emission', 0):,} tok<br>
                            • Model Checking (40% Sink): {wb.get('model_checking_reachability', 0):,} tok<br>
                            • Tests & Substrate (40% Sink): {wb.get('falsification_and_substrate', 0):,} tok
                        </div>
                    </div>
                    """

                if len(p.included_features) <= 4:
                    included_features_markup = f"""
                    <ul style="font-size: 11px; padding-left: 18px; margin: 0 0 10px 0;">
                        {"".join(f"<li>{f}</li>" for f in p.included_features)}
                    </ul>
                    """
                else:
                    first_four = "".join(f"<li>{f}</li>" for f in p.included_features[:4])
                    remaining = "".join(f"<li>{f}</li>" for f in p.included_features[4:])
                    extra_count = len(p.included_features) - 4
                    included_features_markup = f"""
                    <ul style="font-size: 11px; padding-left: 18px; margin: 0 0 4px 0;">
                        {first_four}
                    </ul>
                    <div id="extra-features-{p.tier_id}" style="display: none;">
                        <ul style="font-size: 11px; padding-left: 18px; margin: 0 0 4px 0;">
                            {remaining}
                        </ul>
                    </div>
                    <button onclick="toggleCardFeatures('{p.tier_id}')" id="btn-card-toggle-{p.tier_id}" style="font-size: 11px; padding: 2px 8px; margin-bottom: 8px; color: var(--primary); background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 4px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;">
                        <span>+ {extra_count} more (Click to expand)</span> ▾
                    </button>
                    """

                deferred_markup = ""
                if p.deferred_features:
                    def_list = "".join(f"<li>{f}</li>" for f in p.deferred_features)
                    deferred_markup = f"""
                    <details style="font-size: 11px; color: var(--muted); margin-top: 4px; margin-bottom: 8px;">
                        <summary style="cursor: pointer; color: var(--warning); font-weight: 500;">
                            Cut / Deferred Scope ({len(p.deferred_features)} items)
                        </summary>
                        <ul style="padding-left: 18px; margin: 4px 0 0 0; color: #94a3b8;">
                            {def_list}
                        </ul>
                    </details>
                    """

                cards_html += f"""
                <div class="stat-card" style="{card_border} display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <strong style="color: var(--primary); font-size: 15px;">{p.title}</strong>
                            <span class="badge" style="{badge_style}">{badge_lbl}</span>
                        </div>
                        <div style="font-size: 20px; font-weight: bold; margin-bottom: 2px;">{p.bounded_token_budget:,} tok</div>
                        <div style="font-size: 11px; color: var(--muted); margin-bottom: 8px;">Protected (40%): {p.protected_capital:,} | Exploratory (60%): {p.exploratory_capital:,}</div>
                        {workload_html}
                        <div style="font-size: 12px; margin-bottom: 8px;"><em>{p.target_persona_fit}</em></div>
                        <div style="font-size: 11px; color: var(--muted); margin-bottom: 6px;"><strong>Statechart:</strong> {p.statechart_complexity}</div>
                        <div style="font-size: 11px; margin-bottom: 4px;"><strong>Included Scope:</strong></div>
                        {included_features_markup}
                        {deferred_markup}
                    </div>
                    <div style="font-size: 11px; color: var(--muted); border-top: 1px solid var(--border); padding-top: 8px;">
                        <div><strong>Rationale:</strong> {p.rationale}</div>
                        {f"<div style='margin-top: 6px; color: var(--text);'><strong>Why this budget fits:</strong> {p.token_justification}</div>" if (hasattr(p, 'token_justification') and p.token_justification) else ""}
                    </div>
                </div>
                """

            proposals_html = f"""
            <div class="section">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid var(--border); padding-bottom: 8px;">
                    <h2 style="border: none; padding: 0; margin: 0;">1. Post-Research Project Proposals Matrix (Phase 0-B)</h2>
                    <div class="controls" style="margin: 0;">
                        <button onclick="setProposalView('both')" id="btn-prop-both" class="btn-toggle active">Table & Cards</button>
                        <button onclick="setProposalView('table')" id="btn-prop-table" class="btn-toggle">Table Only</button>
                        <button onclick="setProposalView('cards')" id="btn-prop-cards" class="btn-toggle">Cards Only</button>
                        <button onclick="toggleAllCardScopes()" id="btn-toggle-all-scopes" class="btn-toggle">Expand All Card Scopes</button>
                    </div>
                </div>
                <div style="font-size: 13px; color: var(--muted); margin-bottom: 16px;">
                    Bounded Spectrum: Min {proposal_dossier.min_budget_bound:,} tokens &longleftrightarrow; Safety Max {proposal_dossier.max_safety_budget_bound:,} tokens | Selected Tier: <strong>{proposal_dossier.selected_proposal_id}</strong>
                </div>
                <div id="proposal-table-container" class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th class="col-fit">Tier / Proposal</th>
                                <th class="col-fit col-center">Status</th>
                                <th class="col-fit col-num">Budget Bound</th>
                                <th class="col-fit col-num">Protected (40%)</th>
                                <th class="col-fit col-num">Exploratory (60%)</th>
                                <th class="col-fit">Statechart Complexity</th>
                                <th class="col-auto">Target Persona Fit</th>
                                <th class="col-auto">Included Scope & Deliverables</th>
                                <th class="col-auto">Strategic Rationale</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows_html}
                        </tbody>
                    </table>
                </div>
                <div id="proposal-cards-container" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-top: 16px;">
                    {cards_html}
                </div>
            </div>
            """

        rows_html = ""
        for parent, d_list in decisions_by_node:
            p_self_str = f"Self: {parent.self_allotted:,} tok" if parent.self_allotted > 0 else ""
            p_env_str = f"Env: {parent.token_cost:,} tok" if parent.token_cost > 0 else ""
            p_budget_line = f"<div style='font-size: 10px; color: var(--primary); margin-top: 2px;'>{p_env_str} | {p_self_str}</div>" if p_self_str else ""
            for d in d_list:
                cand_val = d.worker_type.value if hasattr(d.worker_type, "value") else str(d.worker_type)
                cand_name = WORKER_DISPLAY_NAMES.get(cand_val, cand_val)
                badge_class = "badge-chosen" if d.chosen else "badge-rejected"
                badge_text = "CHOSEN" if d.chosen else "SKIPPED"
                allot = f"{d.allotted_tokens:,} tok" if d.chosen else "-"
                used = f"{d.used_tokens:,} tok" if d.chosen else "-"
                eff = f"{(d.used_tokens / d.allotted_tokens * 100):.1f}%" if d.chosen and d.allotted_tokens > 0 else "-"
                rows_html += f"""
                <tr class="{'row-chosen' if d.chosen else 'row-skipped'}">
                    <td class="col-fit">
                        <code>{parent.name}</code>
                        <div style="font-size: 11px; color: var(--muted);">{parent.subgoal or parent.node_id}</div>
                        {p_budget_line}
                    </td>
                    <td class="col-fit"><strong>{cand_name}</strong></td>
                    <td class="col-fit col-center"><span class="badge {badge_class}">{badge_text}</span></td>
                    <td class="col-fit col-num">{allot}</td>
                    <td class="col-fit col-num">{used}</td>
                    <td class="col-fit col-num">{eff}</td>
                    <td class="col-auto"><div class="rationale-text">{d.rationale}</div></td>
                </tr>
                """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meta-Axioma G2b Orchestration Telemetry</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});</script>
    <style>
        :root {{
            --bg: #0f141c;
            --surface: #18202c;
            --border: #2a3649;
            --text: #e2e8f0;
            --muted: #94a3b8;
            --primary: #38bdf8;
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #f87171;
        }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 24px;
            line-height: 1.5;
        }}
        .header {{
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 20px 24px;
            border-radius: 12px;
            margin-bottom: 24px;
        }}
        h1 {{ margin: 0 0 8px 0; font-size: 24px; color: var(--primary); }}
        .meta-bar {{ display: flex; gap: 24px; font-size: 14px; color: var(--muted); }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
        }}
        .stat-val {{ font-size: 24px; font-weight: bold; color: var(--text); margin-top: 4px; }}
        .stat-label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }}
        .section {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
        }}
        h2 {{ margin-top: 0; font-size: 18px; color: var(--primary); border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
        
        /* Responsive Content-Fitting Tables */
        .table-container {{
            width: 100%;
            overflow-x: auto;
            border-radius: 8px;
            border: 1px solid var(--border);
            margin-bottom: 16px;
            background: #0b0f17;
        }}
        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            table-layout: auto;
        }}
        table.data-table th, table.data-table td {{
            padding: 10px 14px;
            border-bottom: 1px solid var(--border);
            vertical-align: middle;
            text-align: left;
        }}
        table.data-table th {{
            background: #141b24;
            color: var(--muted);
            text-transform: uppercase;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.5px;
            position: sticky;
            top: 0;
            z-index: 2;
        }}
        table.data-table tr:last-child td {{
            border-bottom: none;
        }}
        
        /* Column Fitting Utilities */
        .col-fit {{
            white-space: nowrap;
            width: 1%;
        }}
        .col-num {{
            text-align: right !important;
            font-variant-numeric: tabular-nums;
        }}
        .col-center {{
            text-align: center !important;
        }}
        .col-auto {{
            width: auto;
            min-width: 180px;
        }}
        .rationale-text {{
            font-size: 12px;
            color: var(--text);
            line-height: 1.45;
        }}

        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 600;
            white-space: nowrap;
        }}
        .badge-chosen {{ background: rgba(52, 211, 153, 0.2); color: var(--success); border: 1px solid var(--success); }}
        .badge-rejected {{ background: rgba(148, 163, 184, 0.1); color: var(--muted); border: 1px solid var(--muted); }}
        .row-chosen {{ background: rgba(52, 211, 153, 0.03); }}
        .row-chosen:hover {{ background: rgba(52, 211, 153, 0.08); }}
        .row-skipped {{ opacity: 0.7; }}
        .row-skipped:hover {{ opacity: 0.95; background: rgba(255, 255, 255, 0.02); }}

        .controls {{ margin-bottom: 12px; display: flex; gap: 8px; align-items: center; }}
        button {{
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.15s ease;
        }}
        button:hover {{ background: var(--border); color: var(--primary); }}
        .btn-toggle.active {{
            background: rgba(56, 189, 248, 0.2);
            color: var(--primary);
            border-color: var(--primary);
        }}
        .btn-primary {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--primary);
            border: 1px solid var(--primary);
        }}
        .btn-primary:hover {{
            background: var(--primary);
            color: #0b0f17;
        }}

        /* Tree Diagram & Clickable Wrapper */
        .mermaid-wrapper {{
            position: relative;
            cursor: zoom-in;
            background: #080c13;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            overflow-x: auto;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}
        .mermaid-wrapper:hover {{
            border-color: var(--primary);
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.15);
        }}
        .mermaid-badge {{
            position: absolute;
            top: 12px;
            right: 12px;
            background: rgba(24, 32, 44, 0.9);
            border: 1px solid var(--border);
            color: var(--primary);
            font-size: 11px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 9999px;
            pointer-events: none;
            display: flex;
            align-items: center;
            gap: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.4);
            transition: all 0.2s;
        }}
        .mermaid-wrapper:hover .mermaid-badge {{
            background: var(--primary);
            color: #0b0f17;
        }}
        .mermaid {{
            width: 100%;
        }}

        /* Modal Dialog for Interactive Diagram */
        .modal-backdrop {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(11, 15, 23, 0.88);
            backdrop-filter: blur(8px);
            z-index: 9999;
            align-items: center;
            justify-content: center;
            padding: 24px;
            box-sizing: border-box;
        }}
        .modal-dialog {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            width: 95vw;
            height: 90vh;
            max-width: 1600px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 24px 48px rgba(0, 0, 0, 0.7);
            overflow: hidden;
        }}
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 20px;
            border-bottom: 1px solid var(--border);
            background: #141b24;
        }}
        .modal-controls {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        .modal-controls button {{
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            font-weight: 500;
        }}
        .modal-controls button:hover {{
            background: var(--border);
            color: var(--primary);
        }}
        .modal-controls .btn-close {{
            background: rgba(248, 113, 113, 0.15);
            color: var(--danger);
            border: 1px solid var(--danger);
        }}
        .modal-controls .btn-close:hover {{
            background: var(--danger);
            color: #fff;
        }}
        .modal-viewport {{
            flex: 1;
            overflow: hidden;
            position: relative;
            background: #070a0f;
            cursor: grab;
            user-select: none;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .modal-viewport.grabbing {{
            cursor: grabbing;
        }}
        .modal-diagram-canvas {{
            position: absolute;
            transform-origin: center center;
            transition: transform 0.05s ease-out;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .modal-diagram-canvas svg {{
            max-width: none !important;
            height: auto !important;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Meta-Axioma System G2b Orchestration Telemetry</h1>
        <div class="meta-bar">
            <span><strong>Run ID:</strong> {self.run_id}</span>
            <span><strong>Timestamp:</strong> {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</span>
            <span><strong>Max Depth:</strong> {max_depth}</span>
        </div>
    </div>

    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-label">Total Global Budget</div>
            <div class="stat-val">{cost_summary.get('total_budget', 25000) if cost_summary else 25000:,} tok</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Protected Capital (40% Sinks)</div>
            <div class="stat-val" style="color: var(--primary);">{cost_summary.get('protected_spent', 4400) if cost_summary else 4400:,} / {cost_summary.get('protected_reserved', 10000) if cost_summary else 10000:,} tok</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Exploratory Capital (60% Chains)</div>
            <div class="stat-val" style="color: #c084fc;">{cost_summary.get('exploratory_spent', 6500) if cost_summary else 6500:,} / {cost_summary.get('exploratory_reserved', 15000) if cost_summary else 15000:,} tok</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Tokens Allotted / Used</div>
            <div class="stat-val" style="color: var(--success);">{total_allotted:,} / {total_used:,} tok</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Budget Efficiency</div>
            <div class="stat-val">{utilization:.1f}%</div>
        </div>
    </div>

    {proposals_html}

    <div class="section">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 16px;">
            <h2 style="border: none; padding: 0; margin: 0;">2. Recursive Execution Tree DAG</h2>
            <div style="display: flex; gap: 8px; align-items: center;">
                <span style="font-size: 12px; color: var(--muted);">Click diagram to enlarge</span>
                <button onclick="openDiagramModal()" class="btn-primary" style="display: inline-flex; align-items: center; gap: 6px;">
                    🔍 Expand in Interactive Modal
                </button>
            </div>
        </div>
        <div class="mermaid-wrapper" onclick="openDiagramModal()" title="Click to open interactive diagram modal (Zoom / Pan)">
            <div class="mermaid-badge">🔍 Click to Expand Diagram</div>
            <div class="mermaid" id="tree-mermaid">
{dag}
            </div>
        </div>
    </div>

    <div class="section">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 16px;">
            <h2 style="border: none; padding: 0; margin: 0;">3. Orchestrator Subagent Selection & Token Allotment Rationale</h2>
            <div class="controls" style="margin: 0;">
                <button onclick="filterRows('all')" id="btn-filter-all" class="btn-toggle active">Show All</button>
                <button onclick="filterRows('chosen')" id="btn-filter-chosen" class="btn-toggle">Chosen Only</button>
                <button onclick="filterRows('skipped')" id="btn-filter-skipped" class="btn-toggle">Skipped Only</button>
            </div>
        </div>
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th class="col-fit">Parent Node</th>
                        <th class="col-fit">Candidate Subagent</th>
                        <th class="col-fit col-center">Decision</th>
                        <th class="col-fit col-num">Allotment</th>
                        <th class="col-fit col-num">Used</th>
                        <th class="col-fit col-num">Efficiency</th>
                        <th class="col-auto">Selection Rationale</th>
                    </tr>
                </thead>
                <tbody id="decisions-tbody">
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Recursive Tree Diagram Interactive Modal -->
    <div id="diagram-modal" class="modal-backdrop" onclick="handleModalBackdropClick(event)">
        <div class="modal-dialog" onclick="event.stopPropagation()">
            <div class="modal-header">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <h3 style="margin: 0; font-size: 16px; color: var(--primary);">Recursive Execution Tree DAG</h3>
                    <span class="badge" id="modal-zoom-badge" style="background: rgba(148, 163, 184, 0.15); color: var(--text); border: 1px solid var(--border); font-family: monospace;">100%</span>
                </div>
                <div style="font-size: 12px; color: var(--muted); display: flex; gap: 8px;">
                    <span>🖱️ Drag to pan</span>
                    <span>•</span>
                    <span>📜 Scroll to zoom</span>
                    <span>•</span>
                    <span>⌨️ Esc to close</span>
                </div>
                <div class="modal-controls">
                    <button onclick="zoomDiagram(1.25)" title="Zoom in (+)">🔍+ In</button>
                    <button onclick="zoomDiagram(0.8)" title="Zoom out (-)">🔍- Out</button>
                    <button onclick="resetDiagramZoom()" title="Reset scale to 100%">↺ 100%</button>
                    <button onclick="fitDiagramToViewport()" title="Fit to Viewport">⛶ Fit</button>
                    <button class="btn-close" onclick="closeDiagramModal()" title="Close viewer (Esc)">✕ Close</button>
                </div>
            </div>
            <div id="modal-viewport" class="modal-viewport" onmousedown="startPan(event)">
                <div id="modal-diagram-canvas" class="modal-diagram-canvas"></div>
            </div>
        </div>
    </div>

    <script>
        function filterRows(type) {{
            const rows = document.querySelectorAll('#decisions-tbody tr');
            rows.forEach(r => {{
                if (type === 'all') r.style.display = '';
                else if (type === 'chosen') r.style.display = r.classList.contains('row-chosen') ? '' : 'none';
                else if (type === 'skipped') r.style.display = r.classList.contains('row-skipped') ? '' : 'none';
            }});
            ['all', 'chosen', 'skipped'].forEach(t => {{
                const btn = document.getElementById('btn-filter-' + t);
                if (btn) {{
                    if (t === type) btn.classList.add('active');
                    else btn.classList.remove('active');
                }}
            }});
        }}

        function setProposalView(view) {{
            const tbl = document.getElementById('proposal-table-container');
            const cards = document.getElementById('proposal-cards-container');
            if (tbl && cards) {{
                if (view === 'both') {{
                    tbl.style.display = '';
                    cards.style.display = 'grid';
                }} else if (view === 'table') {{
                    tbl.style.display = '';
                    cards.style.display = 'none';
                }} else if (view === 'cards') {{
                    tbl.style.display = 'none';
                    cards.style.display = 'grid';
                }}
            }}
            ['both', 'table', 'cards'].forEach(v => {{
                const btn = document.getElementById('btn-prop-' + v);
                if (btn) {{
                    if (v === view) btn.classList.add('active');
                    else btn.classList.remove('active');
                }}
            }});
        }}

        function toggleCardFeatures(tierId) {{
            const el = document.getElementById('extra-features-' + tierId);
            const btn = document.getElementById('btn-card-toggle-' + tierId);
            if (!el || !btn) return;
            if (el.style.display === 'none') {{
                el.style.display = 'block';
                btn.innerHTML = '<span>Show less</span> ▴';
                btn.style.background = 'rgba(148, 163, 184, 0.15)';
                btn.style.color = 'var(--text)';
                btn.style.borderColor = 'var(--border)';
            }} else {{
                el.style.display = 'none';
                const count = el.querySelectorAll('li').length;
                btn.innerHTML = '<span>+ ' + count + ' more (Click to expand)</span> ▾';
                btn.style.background = 'rgba(56, 189, 248, 0.1)';
                btn.style.color = 'var(--primary)';
                btn.style.borderColor = 'rgba(56, 189, 248, 0.3)';
            }}
        }}

        let allScopesExpanded = false;
        function toggleAllCardScopes() {{
            allScopesExpanded = !allScopesExpanded;
            const extraEls = document.querySelectorAll('[id^="extra-features-"]');
            extraEls.forEach(el => {{
                const tierId = el.id.replace('extra-features-', '');
                const btn = document.getElementById('btn-card-toggle-' + tierId);
                if (allScopesExpanded) {{
                    el.style.display = 'block';
                    if (btn) {{
                        btn.innerHTML = '<span>Show less</span> ▴';
                        btn.style.background = 'rgba(148, 163, 184, 0.15)';
                        btn.style.color = 'var(--text)';
                        btn.style.borderColor = 'var(--border)';
                    }}
                }} else {{
                    el.style.display = 'none';
                    if (btn) {{
                        const count = el.querySelectorAll('li').length;
                        btn.innerHTML = '<span>+ ' + count + ' more (Click to expand)</span> ▾';
                        btn.style.background = 'rgba(56, 189, 248, 0.1)';
                        btn.style.color = 'var(--primary)';
                        btn.style.borderColor = 'rgba(56, 189, 248, 0.3)';
                    }}
                }}
            }});
            const toggleAllBtn = document.getElementById('btn-toggle-all-scopes');
            if (toggleAllBtn) {{
                toggleAllBtn.textContent = allScopesExpanded ? 'Collapse All Card Scopes' : 'Expand All Card Scopes';
                if (allScopesExpanded) toggleAllBtn.classList.add('active');
                else toggleAllBtn.classList.remove('active');
            }}
        }}

        // --- Interactive Modal Logic ---
        let currentScale = 1.0;
        let panX = 0;
        let panY = 0;
        let isPanning = false;
        let startMouseX = 0;
        let startMouseY = 0;
        let startPanX = 0;
        let startPanY = 0;

        function updateCanvasTransform() {{
            const canvas = document.getElementById('modal-diagram-canvas');
            if (canvas) {{
                canvas.style.transform = 'translate(' + panX + 'px, ' + panY + 'px) scale(' + currentScale + ')';
            }}
            const badge = document.getElementById('modal-zoom-badge');
            if (badge) {{
                badge.textContent = Math.round(currentScale * 100) + '%';
            }}
        }}

        function openDiagramModal() {{
            const modal = document.getElementById('diagram-modal');
            const target = document.getElementById('modal-diagram-canvas');
            const originalSvg = document.querySelector('#tree-mermaid svg') || document.querySelector('.mermaid svg');
            if (!originalSvg) {{
                alert('The diagram SVG is still initializing. Please wait a moment and try again.');
                return;
            }}
            target.innerHTML = '';
            const clone = originalSvg.cloneNode(true);
            clone.removeAttribute('id');
            clone.style.maxWidth = 'none';
            clone.style.width = 'auto';
            clone.style.height = 'auto';
            target.appendChild(clone);

            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';

            // Auto-fit after modal renders
            setTimeout(() => {{
                fitDiagramToViewport();
            }}, 30);
        }}

        function closeDiagramModal() {{
            const modal = document.getElementById('diagram-modal');
            if (modal) modal.style.display = 'none';
            document.body.style.overflow = '';
        }}

        function handleModalBackdropClick(e) {{
            if (e.target.id === 'diagram-modal') {{
                closeDiagramModal();
            }}
        }}

        function zoomDiagram(factor) {{
            currentScale = Math.min(Math.max(currentScale * factor, 0.15), 6.0);
            updateCanvasTransform();
        }}

        function resetDiagramZoom() {{
            currentScale = 1.0;
            panX = 0;
            panY = 0;
            updateCanvasTransform();
        }}

        function fitDiagramToViewport() {{
            const canvas = document.getElementById('modal-diagram-canvas');
            const viewport = document.getElementById('modal-viewport');
            const svg = canvas ? canvas.querySelector('svg') : null;
            if (!svg || !viewport) return;
            const vRect = viewport.getBoundingClientRect();
            let sWidth = 1400;
            let sHeight = 800;
            if (svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width > 0) {{
                sWidth = svg.viewBox.baseVal.width;
                sHeight = svg.viewBox.baseVal.height;
            }} else if (svg.getBBox) {{
                try {{
                    const bbox = svg.getBBox();
                    sWidth = bbox.width || 1400;
                    sHeight = bbox.height || 800;
                }} catch (e) {{}}
            }}
            const scaleX = (vRect.width - 60) / sWidth;
            const scaleY = (vRect.height - 60) / sHeight;
            currentScale = Math.min(Math.max(Math.min(scaleX, scaleY), 0.25), 2.5);
            panX = 0;
            panY = 0;
            updateCanvasTransform();
        }}

        function startPan(e) {{
            if (e.button !== 0) return;
            isPanning = true;
            startMouseX = e.clientX;
            startMouseY = e.clientY;
            startPanX = panX;
            startPanY = panY;
            const viewport = document.getElementById('modal-viewport');
            if (viewport) viewport.classList.add('grabbing');
            e.preventDefault();
        }}

        window.addEventListener('mousemove', function(e) {{
            if (!isPanning) return;
            panX = startPanX + (e.clientX - startMouseX);
            panY = startPanY + (e.clientY - startMouseY);
            updateCanvasTransform();
        }});

        window.addEventListener('mouseup', function(e) {{
            if (isPanning) {{
                isPanning = false;
                const viewport = document.getElementById('modal-viewport');
                if (viewport) viewport.classList.remove('grabbing');
            }}
        }});

        // Wheel zoom inside modal
        document.addEventListener('wheel', function(e) {{
            const modal = document.getElementById('diagram-modal');
            if (modal && modal.style.display === 'flex') {{
                const viewport = document.getElementById('modal-viewport');
                if (viewport && viewport.contains(e.target)) {{
                    e.preventDefault();
                    const factor = e.deltaY < 0 ? 1.12 : 0.89;
                    currentScale = Math.min(Math.max(currentScale * factor, 0.15), 6.0);
                    updateCanvasTransform();
                }}
            }}
        }}, {{ passive: false }});

        // Keyboard escape
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                closeDiagramModal();
            }}
        }});
    </script>
</body>
</html>
"""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(html_content, encoding="utf-8")

    def _sum_allotted_tokens(self, node: RecursionNode) -> int:
        child_sum = sum(self._sum_allotted_tokens(c) for c in node.children)
        if node.token_cost >= (node.self_allotted or 0) + child_sum:
            return node.token_cost
        return (node.self_allotted or node.token_cost) + child_sum

    def _sum_used_tokens(self, node: RecursionNode) -> int:
        child_used = sum(self._sum_used_tokens(c) for c in node.children)
        current_used = node.tokens_used or node.self_used or node.token_cost
        if current_used >= (node.self_used or 0) + child_used:
            return current_used
        return (node.self_used or current_used) + child_used

    def _max_depth(self, node: RecursionNode) -> int:
        return max([node.depth] + [self._max_depth(c) for c in node.children])

    def _collect_opinions(self, node: RecursionNode) -> List[tuple]:
        res = []
        if node.boundary_opinion:
            res.append((node, node.boundary_opinion))
        for c in node.children:
            res.extend(self._collect_opinions(c))
        return res

    def _collect_all_decisions(self, node: RecursionNode) -> List[tuple]:
        res = []
        if node.selection_decisions:
            res.append((node, node.selection_decisions))
        for c in node.children:
            res.extend(self._collect_all_decisions(c))
        return res
