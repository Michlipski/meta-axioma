"""Causal Reactive Pipeline Benchmark Runner.

Programmatically drives multi-agent benchmark trials:
- Connects live synthesis engines to the MacroEvaluationGauntlet.
- Enforces Pass 0 Multi-Agent Provenance & Context Separation.
- Generates JSON telemetry ledgers and standalone zero-CDN visual dashboards.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Callable, Dict, List, Optional

from benchmarks.macro_ablation.archetypes import get_archetype_by_id
from benchmarks.macro_ablation.domain_models import (
    AblationMode,
    BenchmarkArchetype,
    MacroScorecard,
)
from benchmarks.macro_ablation.macro_evaluator import MacroEvaluationGauntlet
from .synthesis_engines import (
    AxiomaCausalMeshEngine,
    BaseSynthesisEngine,
    SynthesisResult,
    VanillaSynthesisEngine,
)


@dataclass
class BenchmarkTrialConfig:
    """Configuration for a single candidate benchmark trial."""
    system_id: str
    system_name: str
    archetype_id: str
    trial: int
    target_dir: Path
    mode: AblationMode = AblationMode.FULL_G4B
    contract_parity: Optional[bool] = None


@dataclass
class BenchmarkRunResult:
    """Outcome of an individual benchmark trial."""
    config: BenchmarkTrialConfig
    synthesis_result: SynthesisResult
    scorecard: MacroScorecard


class CausalPipelineRunner:
    """Deterministic orchestrator for multi-agent benchmark runs."""

    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        enable_provenance: bool = True,
        reports_dir: Optional[Path] = None,
        vanilla_contract_parity: bool = True,
    ) -> None:
        if workspace_root:
            self.workspace_root = Path(workspace_root).resolve()
        else:
            self.workspace_root = Path(__file__).resolve().parent.parent.parent

        self.reports_dir = (
            Path(reports_dir).resolve()
            if reports_dir
            else self.workspace_root / "benchmarks" / "reports"
        )
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.enable_provenance = enable_provenance
        self.vanilla_contract_parity = bool(vanilla_contract_parity)
        self.gauntlet = MacroEvaluationGauntlet(enable_provenance=enable_provenance)

    def select_engine(
        self,
        system_id: str,
        contract_parity: Optional[bool] = None,
    ) -> BaseSynthesisEngine:
        """Returns the appropriate synthesis engine based on system_id."""
        sys_id = system_id.lower()
        effective_parity = (
            self.vanilla_contract_parity if contract_parity is None else bool(contract_parity)
        )
        if "axioma" in sys_id:
            return AxiomaCausalMeshEngine(system_id=system_id)
        elif "vanilla" in sys_id:
            return VanillaSynthesisEngine(system_id=system_id, contract_parity=effective_parity)
        else:
            return VanillaSynthesisEngine(system_id=system_id, contract_parity=effective_parity)

    def run_trial(
        self,
        config: BenchmarkTrialConfig,
        subagent_invoker: Optional[Callable[[str, str, str], str]] = None,
    ) -> BenchmarkRunResult:
        """Executes synthesis, physical disk grounding, and multi-pass evaluation for a single trial."""
        archetype = get_archetype_by_id(config.archetype_id)
        engine = self.select_engine(config.system_id, contract_parity=config.contract_parity)

        # 1. Synthesis Phase
        synth_result = engine.synthesize(
            archetype=archetype,
            target_dir=config.target_dir,
            subagent_invoker=subagent_invoker,
        )

        # 2. Evaluation Gauntlet Phase (Pass 0 through Pass 5)
        scorecard = self.gauntlet.evaluate_app(
            app_dir=config.target_dir,
            archetype=archetype,
            mode=config.mode,
            provenance_manifest=synth_result.manifest,
        )

        return BenchmarkRunResult(
            config=config,
            synthesis_result=synth_result,
            scorecard=scorecard,
        )

    def run_benchmark_matrix(
        self,
        trial_configs: List[BenchmarkTrialConfig],
        subagent_invoker: Optional[Callable[[str, str, str], str]] = None,
        report_prefix: str = "causal_pilot",
    ) -> Dict[str, Any]:
        """Executes a full multi-system, multi-trial benchmark matrix."""
        results: List[BenchmarkRunResult] = []
        summary_by_system: Dict[str, Dict[str, Any]] = {}

        for cfg in trial_configs:
            sys_name = cfg.system_name
            if sys_name not in summary_by_system:
                summary_by_system[sys_name] = {
                    "system_id": cfg.system_id,
                    "runs": 0,
                    "scores": [],
                    "liveness_passes": 0,
                    "provenance_passes": 0,
                }

            run_res = self.run_trial(cfg, subagent_invoker=subagent_invoker)
            results.append(run_res)

            sc = run_res.scorecard
            summary_by_system[sys_name]["runs"] += 1
            summary_by_system[sys_name]["scores"].append(sc.composite_score)
            if sc.tier0_liveness.passed:
                summary_by_system[sys_name]["liveness_passes"] += 1
            if "provenance" in sc.pass_results and sc.pass_results["provenance"].passed:
                summary_by_system[sys_name]["provenance_passes"] += 1

        # Calculate statistics
        for sname, data in summary_by_system.items():
            scs = data["scores"]
            data["mean"] = round(sum(scs) / len(scs), 2) if scs else 0.0
            data["min"] = min(scs) if scs else 0.0
            data["max"] = max(scs) if scs else 0.0
            data["variance_delta"] = round(data["max"] - data["min"], 2)

        ledger_payload = {
            "report_id": f"rpt_{report_prefix}_{int(time.time())}",
            "timestamp": int(time.time()),
            "enable_provenance": self.enable_provenance,
            "vanilla_contract_parity": self.vanilla_contract_parity,
            "total_runs": len(results),
            "summary_by_system": summary_by_system,
            "runs": [
                {
                    "system_id": r.config.system_id,
                    "system_name": r.config.system_name,
                    "trial": r.config.trial,
                    "target_dir": str(r.config.target_dir),
                    "contract_parity": r.synthesis_result.manifest.get("contract_parity"),
                    "subagents": r.synthesis_result.subagent_witnesses,
                    "scorecard": r.scorecard.to_dict(),
                }
                for r in results
            ],
        }

        # Emit JSON ledger
        ledger_file = self.reports_dir / f"{report_prefix}_ledger.json"
        ledger_file.write_text(json.dumps(ledger_payload, indent=2), encoding="utf-8")

        # Emit HTML visual dashboard
        dashboard_file = self.reports_dir / f"{report_prefix}_dashboard.html"
        self._generate_dashboard_html(ledger_payload, dashboard_file)

        return ledger_payload

    def _generate_dashboard_html(self, payload: Dict[str, Any], output_path: Path) -> Path:
        """Generates a standalone zero-CDN visual HTML dashboard for benchmark results."""
        summary = payload.get("summary_by_system", {})
        runs = payload.get("runs", [])

        summary_rows = ""
        for sname, sdata in summary.items():
            summary_rows += f"""
                <tr>
                    <td><strong>{sname}</strong></td>
                    <td>{sdata['runs']}</td>
                    <td>{sdata['liveness_passes']} / {sdata['runs']}</td>
                    <td>{sdata['provenance_passes']} / {sdata['runs']}</td>
                    <td><strong style="color:var(--accent);">{sdata['mean']:.2f}</strong> / 100</td>
                    <td>Δ = {sdata['variance_delta']:.2f} pts</td>
                </tr>
            """

        card_panels = ""
        for r in runs:
            sc = r["scorecard"]
            passes_rows = ""
            for pname, pres in sc.get("pass_results", {}).items():
                pstatus = "pass" if pres.get("passed", False) else "fail"
                if pname == "provenance":
                    weight_label = "GATE (0.0x / 1.0x)"
                    weighted_val = "1.0x MULT" if pres.get("passed", False) else "0.0x (DISQUALIFIED)"
                elif pname == "adversarial_integrity":
                    weight_label = "PENALTY / CAP"
                    pen = pres.get("details", {}).get("penalty_points", 0.0)
                    cap = pres.get("details", {}).get("score_cap", 100.0)
                    weighted_val = f"-{pen:.1f} pts (cap {cap:.0f})"
                else:
                    weight_label = f"{pres.get('weight', 0.0) * 100:.0f}%"
                    weighted_val = f"{pres.get('weighted_score', 0.0):.2f}"

                passes_rows += f"""
                    <tr>
                        <td><code>{pname}</code></td>
                        <td>{weight_label}</td>
                        <td>{pres.get('raw_score', 0.0):.1f}%</td>
                        <td><strong>{weighted_val}</strong></td>
                        <td><span class="badge {pstatus}">{pstatus.upper()}</span></td>
                    </tr>
                """

            subagents_html = ""
            for s in r.get("subagents", []):
                subagents_html += f"<li><strong>{s.get('role')}</strong>: <code>{s.get('conversation_id', '')[:12]}...</code></li>"

            prov_mult = sc.get("provenance_multiplier", 1.0)
            prov_badge = '<span class="badge pass">PROVENANCE PASS</span>' if prov_mult == 1.0 else '<span class="badge fail">PROVENANCE FAIL</span>'
            liveness_badge = '<span class="badge pass">LIVENESS PASS</span>' if sc.get("tier0_multiplier", 1.0) == 1.0 else '<span class="badge fail">LIVENESS FAIL</span>'

            card_panels += f"""
                <div class="scorecard-panel">
                    <div class="scorecard-header">
                        <h3>{r['system_name']} (Trial {r['trial']})</h3>
                        <div style="display:flex; gap:0.5rem;">
                            {liveness_badge}
                            {prov_badge}
                        </div>
                    </div>
                    <div class="score-display">
                        <span class="composite-value">{sc.get('composite_score', 0.0):.2f}</span>
                        <span class="graded-sub">/ 100.0</span>
                    </div>
                    <table class="pass-table">
                        <thead>
                            <tr><th>Pass</th><th>Weight</th><th>Raw</th><th>Weighted</th><th>Status</th></tr>
                        </thead>
                        <tbody>{passes_rows}</tbody>
                    </table>
                    <div class="subagents-box">
                        <strong>Subagent Context Witnesses ({len(r.get('subagents', []))}):</strong>
                        <ul>{subagents_html}</ul>
                    </div>
                </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Meta-Axioma Causal Multi-Agent Benchmark Dashboard</title>
    <style>
        :root {{
            --bg: #0d1117;
            --surface: #161b22;
            --border: #30363d;
            --text: #c9d1d9;
            --text-bright: #f0f6fc;
            --accent: #58a6ff;
            --green: #3fb950;
            --red: #f85149;
            --orange: #f0883e;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 24px;
            line-height: 1.5;
        }}
        h1, h2, h3 {{ color: var(--text-bright); }}
        .summary-table, .pass-table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--surface);
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid var(--border);
            margin-top: 12px;
        }}
        th, td {{ padding: 12px 16px; border-bottom: 1px solid var(--border); text-align: left; }}
        th {{ background: #21262d; color: var(--text-bright); font-size: 12px; text-transform: uppercase; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
        .badge.pass {{ background: rgba(63, 185, 80, 0.2); color: var(--green); }}
        .badge.fail {{ background: rgba(248, 81, 73, 0.2); color: var(--red); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 20px; margin-top: 20px; }}
        .scorecard-panel {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; }}
        .scorecard-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 12px; }}
        .composite-value {{ font-size: 38px; font-weight: bold; color: var(--accent); font-family: monospace; }}
        .graded-sub {{ color: #8b949e; font-size: 14px; margin-left: 8px; }}
        .subagents-box {{ margin-top: 16px; padding: 12px; background: #0d1117; border: 1px solid var(--border); border-radius: 6px; font-size: 12px; }}
        .subagents-box ul {{ margin: 6px 0 0 0; padding-left: 20px; }}
    </style>
</head>
<body>
    <h1>Meta-Axioma Causal Multi-Agent Benchmark Dashboard</h1>
    <p>Report ID: <code>{payload.get('report_id')}</code> | Total Runs: <code>{payload.get('total_runs')}</code></p>

    <h2>1. Executive Summary & Epistemic Separation</h2>
    <table class="summary-table">
        <thead>
            <tr><th>System</th><th>Runs</th><th>Liveness Passed</th><th>Provenance Passed</th><th>Mean Score</th><th>Variance</th></tr>
        </thead>
        <tbody>{summary_rows}</tbody>
    </table>

    <h2>2. Grounded Scorecards</h2>
    <div class="grid">{card_panels}</div>
</body>
</html>
"""
        output_path.write_text(html_content, encoding="utf-8")
        return output_path
