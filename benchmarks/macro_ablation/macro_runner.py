"""CLI Runner and Benchmark Orchestrator for Meta-Axioma Macro-Bench.

Supports:
- Evaluation of built-in archetypes across all 5 ablation modes.
- Evaluation of external applications against specific archetypes.
- Standard GitHub Flavored Markdown matrix output and JSON telemetry ledger.
- Generation of standalone zero-CDN HTML dashboard.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Dict, List, Optional

from .archetypes import ALL_ARCHETYPE_MODULES, get_all_archetypes, get_archetype_by_id
from .domain_models import (
    AblationMode,
    BenchmarkArchetype,
    MacroBenchmarkReport,
    MacroScorecard,
)
from .macro_evaluator import MacroEvaluationGauntlet


class MacroRunner:
    """Orchestrates multi-archetype ablation benchmark runs."""

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        if workspace_root:
            self.workspace_root = Path(workspace_root).resolve()
        else:
            self.workspace_root = Path(__file__).resolve().parent.parent.parent

        self.scratch_dir = self.workspace_root / ".scratch" / "macro_bench"
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        self.gauntlet = MacroEvaluationGauntlet()

    def run_benchmark(
        self,
        archetype_ids: Optional[List[str]] = None,
        modes: Optional[List[AblationMode]] = None,
    ) -> MacroBenchmarkReport:
        """Executes the benchmark across specified archetypes and ablation modes."""
        if not archetype_ids or "all" in archetype_ids:
            archetype_ids = list(ALL_ARCHETYPE_MODULES.keys())

        if not modes:
            modes = [
                AblationMode.FULL_G4B,
                AblationMode.FLAT_PROMPT_LLM,
                AblationMode.WO_CONTRACTS_SMT,
                AblationMode.WO_AST_AUDITORS,
                AblationMode.WO_SUBPROCESS_SMOKE,
            ]

        scorecards: List[MacroScorecard] = []
        summary_matrix: Dict[str, Dict[str, float]] = {}

        for arch_id in archetype_ids:
            summary_matrix[arch_id] = {}
            mod = ALL_ARCHETYPE_MODULES.get(arch_id)
            if not mod:
                continue
            archetype = mod.get_archetype()

            for mode in modes:
                # Generate candidate application in designated scratch directory
                candidate_dir = self.scratch_dir / f"{arch_id}_{mode.value}"
                mod.generate_candidate_app(mode, candidate_dir)

                # Evaluate candidate app
                scorecard = self.gauntlet.evaluate_app(candidate_dir, archetype, mode)
                scorecards.append(scorecard)
                summary_matrix[arch_id][mode.value] = scorecard.composite_score

        report_id = f"rpt_macro_{int(time.time())}"
        return MacroBenchmarkReport(
            report_id=report_id,
            timestamp=time.time(),
            scorecards=scorecards,
            summary_matrix=summary_matrix,
        )

    def evaluate_external_app(
        self,
        app_dir: Path,
        archetype_id: str,
        mode: AblationMode = AblationMode.FULL_G4B,
    ) -> MacroScorecard:
        """Evaluates an external application target against a designated archetype."""
        archetype = get_archetype_by_id(archetype_id)
        return self.gauntlet.evaluate_app(app_dir, archetype, mode)

    def generate_dashboard_html(self, report: MacroBenchmarkReport, output_file: Path) -> Path:
        """Emits a zero-CDN standalone HTML dashboard visualizing macro benchmark results."""
        matrix_rows = []
        for arch, scores in report.summary_matrix.items():
            matrix_rows.append(f"""
                <tr>
                    <td class="archetype-name">{arch}</td>
                    <td class="score-cell baseline">{scores.get('full_g4b', 0.0):.1f}</td>
                    <td class="score-cell ablated">{scores.get('flat_prompt_llm', 0.0):.1f}</td>
                    <td class="score-cell ablated">{scores.get('wo_contracts_smt', 0.0):.1f}</td>
                    <td class="score-cell ablated">{scores.get('wo_ast_auditors', 0.0):.1f}</td>
                    <td class="score-cell smoke">{scores.get('wo_subprocess_smoke', 0.0):.1f}</td>
                </tr>
            """)

        cards_html = []
        for sc in report.scorecards:
            liveness_badge = (
                '<span class="badge pass">LIVENESS PASS</span>'
                if sc.tier0_liveness.passed
                else '<span class="badge fail">LIVENESS FAIL (0.0x)</span>'
            )
            passes_rows = []
            for pname, pres in sc.pass_results.items():
                pstatus = "pass" if pres.passed else "fail"
                passes_rows.append(f"""
                    <tr>
                        <td><code>{pname}</code></td>
                        <td>{pres.weight * 100:.0f}%</td>
                        <td>{pres.raw_score:.1f}</td>
                        <td><strong>{pres.weighted_score:.2f}</strong></td>
                        <td><span class="badge {pstatus}">{pstatus.upper()}</span></td>
                    </tr>
                """)

            cards_html.append(f"""
                <div class="scorecard-panel">
                    <div class="scorecard-header">
                        <h3>{sc.archetype_id} — {sc.ablation_mode.value}</h3>
                        <div>{liveness_badge}</div>
                    </div>
                    <div class="score-display">
                        <span class="composite-value">{sc.composite_score:.1f}</span>
                        <span class="graded-sub">/ 100 (Graded: {sc.graded_score:.1f})</span>
                    </div>
                    <table class="pass-table">
                        <thead>
                            <tr><th>Pass</th><th>Weight</th><th>Raw</th><th>Weighted</th><th>Status</th></tr>
                        </thead>
                        <tbody>
                            {''.join(passes_rows)}
                        </tbody>
                    </table>
                </div>
            """)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Axioma Macro-Bench: Application Ablation Cockpit</title>
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
            --yellow: #d29922;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 24px;
        }}
        .header {{
            border-bottom: 1px solid var(--border);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        h1, h2, h3 {{ color: var(--text-bright); }}
        .matrix-table, .pass-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
            background: var(--surface);
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{ background: #21262d; color: var(--text-bright); font-size: 13px; text-transform: uppercase; }}
        .score-cell {{ font-weight: bold; font-family: monospace; font-size: 14px; }}
        .score-cell.baseline {{ color: var(--green); }}
        .score-cell.ablated {{ color: var(--yellow); }}
        .score-cell.smoke {{ color: var(--red); }}
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }}
        .badge.pass {{ background: rgba(63, 185, 80, 0.2); color: var(--green); }}
        .badge.fail {{ background: rgba(248, 81, 73, 0.2); color: var(--red); }}
        .scorecard-panel {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }}
        .scorecard-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
        }}
        .composite-value {{
            font-size: 32px;
            font-weight: bold;
            color: var(--accent);
            font-family: monospace;
        }}
        .graded-sub {{ color: #8b949e; font-size: 14px; margin-left: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Axioma Macro-Bench: Application Ablation Cockpit</h1>
        <p>Report ID: <code>{report.report_id}</code> | Timestamp: <code>{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(report.timestamp))} UTC</code></p>
    </div>

    <h2>1. Executive Ablation Matrix</h2>
    <table class="matrix-table">
        <thead>
            <tr>
                <th>Archetype</th>
                <th>Full G4b (Baseline)</th>
                <th>Ablation 1 (Flat LLM)</th>
                <th>Ablation 2 (w/o Contracts)</th>
                <th>Ablation 3 (w/o Auditors)</th>
                <th>Ablation 4 (w/o Smoke Gate)</th>
            </tr>
        </thead>
        <tbody>
            {''.join(matrix_rows)}
        </tbody>
    </table>

    <h2 style="margin-top: 36px;">2. Detailed Evaluation Scorecards</h2>
    {''.join(cards_html)}
</body>
</html>
"""
        output_file.write_text(html_content, encoding="utf-8")
        return output_file


def main():
    parser = argparse.ArgumentParser(description="Meta-Axioma Macro-Bench Runner")
    parser.add_argument(
        "--archetype",
        type=str,
        default="all",
        help="Target archetype: [kv|flow|collab|gateway|all]",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["markdown", "json"],
        default="markdown",
        help="Output format: [markdown|json]",
    )
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    parser.add_argument(
        "--dashboard",
        type=str,
        default="benchmarks/macro_ablation/macro_dashboard.html",
        help="Path to generate standalone HTML dashboard",
    )
    parser.add_argument("--app-dir", type=str, default=None, help="Evaluate external application directory")
    args = parser.parse_args()

    runner = MacroRunner()

    if args.app_dir:
        app_path = Path(args.app_dir).resolve()
        arch_id = "axioma_kv" if args.archetype == "all" else args.archetype
        if not arch_id.startswith("axioma_"):
            arch_id = f"axioma_{arch_id}"
        scorecard = runner.evaluate_external_app(app_path, arch_id)
        if args.format == "json":
            out_str = json.dumps(scorecard.to_dict(), indent=2)
        else:
            out_str = f"# Evaluation Scorecard for {app_path.name}\n" + json.dumps(scorecard.to_dict(), indent=2)
        print(out_str)
        if args.output:
            Path(args.output).write_text(out_str, encoding="utf-8")
        return

    # Map shortcut argument
    arch_map = {
        "kv": "axioma_kv",
        "flow": "axioma_flow",
        "collab": "axioma_collab",
        "gateway": "axioma_gateway",
        "all": "all",
    }
    target_arch = arch_map.get(args.archetype, args.archetype)
    target_archs = ["all"] if target_arch == "all" else [target_arch]

    print(f"[*] Starting Axioma Macro-Bench execution for archetypes: {target_archs} ...", file=sys.stderr)
    report = runner.run_benchmark(archetype_ids=target_archs)

    # Generate dashboard HTML
    if args.dashboard:
        dash_path = runner.workspace_root / args.dashboard
        runner.generate_dashboard_html(report, dash_path)
        print(f"[+] Macro dashboard emitted to {dash_path}", file=sys.stderr)

    if args.format == "json":
        output_str = json.dumps(report.to_dict(), indent=2)
    else:
        output_str = report.to_markdown()

    if args.output:
        out_p = Path(args.output)
        out_p.write_text(output_str, encoding="utf-8")
        print(f"[+] Benchmark report saved to {out_p}", file=sys.stderr)

    print(output_str)


if __name__ == "__main__":
    main()
