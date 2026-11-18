"""Stage 1 Pilot Benchmark Runner (`benchmarks/stage1_pilot_runner.py`).

Executes the approved Stage 1 Pilot Plan:
- 2 Systems: Meta-Axioma G4b Baseline vs Antigravity Vanilla
- 1 Archetype: Axioma-KV (Transactional Key-Value Store with WAL & REST)
- 2 Trials per system ($N=2$, 4 runs total)
- Ephemeral execution in `.scratch/benchmarks/stage1_pilot/`
- Tier 0 Operational Liveness Gatekeeper ([NEG-G1B-002])
- Cryptographic SHA-256 Merkle sealing
- Generates:
    - `benchmarks/reports/stage1_pilot_ledger.json`
    - `benchmarks/reports/stage1_pilot_dashboard.html`
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from benchmarks.macro_ablation.archetypes import axioma_kv
from benchmarks.macro_ablation.domain_models import (
    AblationMode,
    BenchmarkArchetype,
    EvaluationPassResult,
    MacroScorecard,
    Tier0LivenessResult,
)
from benchmarks.macro_ablation.macro_evaluator import MacroEvaluationGauntlet


@dataclass
class Stage1PilotReport:
    """Consolidated report for the Stage 1 Pilot run."""
    report_id: str
    timestamp: float
    merkle_root: str
    total_runs: int
    scorecards: List[MacroScorecard]
    summary_by_system: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "merkle_root": self.merkle_root,
            "total_runs": self.total_runs,
            "scorecards": [s.to_dict() for s in self.scorecards],
            "summary_by_system": self.summary_by_system,
        }


def compute_harness_merkle_root(base_dir: Path) -> str:
    """Computes a SHA-256 Merkle root across all evaluators and archetype definitions."""
    hasher = hashlib.sha256()
    eval_dir = base_dir / "benchmarks" / "macro_ablation" / "evaluators"
    arch_dir = base_dir / "benchmarks" / "macro_ablation" / "archetypes"

    target_files = sorted(list(eval_dir.glob("*.py")) + list(arch_dir.glob("*.py")))
    for tf in target_files:
        hasher.update(tf.read_bytes())
    return hasher.hexdigest()


class Stage1PilotRunner:
    """Orchestrates the 4-run Stage 1 Pilot gauntlet."""

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        if workspace_root:
            self.workspace_root = Path(workspace_root).resolve()
        else:
            self.workspace_root = Path(__file__).resolve().parent.parent

        self.scratch_dir = self.workspace_root / ".scratch" / "benchmarks" / "stage1_pilot"
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = self.workspace_root / "benchmarks" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.gauntlet = MacroEvaluationGauntlet()

    def run_pilot(self) -> Stage1PilotReport:
        merkle_root = compute_harness_merkle_root(self.workspace_root)
        archetype = axioma_kv.get_archetype()
        report_id = f"rpt_stage1_{int(time.time())}"

        runs_config = [
            {
                "system_name": "Meta-Axioma G4b Baseline",
                "system_id": "meta_axioma_g4b",
                "trial": 1,
                "mode": AblationMode.FULL_G4B,
                "run_id": "run_01_axioma_t1",
            },
            {
                "system_name": "Meta-Axioma G4b Baseline",
                "system_id": "meta_axioma_g4b",
                "trial": 2,
                "mode": AblationMode.FULL_G4B,
                "run_id": "run_02_axioma_t2",
            },
            {
                "system_name": "Antigravity Vanilla",
                "system_id": "antigravity_vanilla",
                "trial": 1,
                "mode": AblationMode.FLAT_PROMPT_LLM,
                "run_id": "run_03_vanilla_t1",
            },
            {
                "system_name": "Antigravity Vanilla",
                "system_id": "antigravity_vanilla",
                "trial": 2,
                "mode": AblationMode.WO_SUBPROCESS_SMOKE,
                "run_id": "run_04_vanilla_t2",
            },
        ]

        scorecards: List[MacroScorecard] = []
        summary_by_system: Dict[str, Dict[str, Any]] = {
            "Meta-Axioma G4b Baseline": {"scores": [], "liveness_passes": 0, "runs": 0},
            "Antigravity Vanilla": {"scores": [], "liveness_passes": 0, "runs": 0},
        }

        print(f"\n========================================================")
        print(f"  EXECUTING STAGE 1 PILOT BENCHMARK GAUNTLET")
        print(f"  Report ID: {report_id} | Merkle: {merkle_root[:16]}...")
        print(f"  2 Systems x 1 Archetype (Axioma-KV) x 2 Trials = 4 Runs")
        print(f"========================================================\n")

        for cfg in runs_config:
            system_name = cfg["system_name"]
            trial = cfg["trial"]
            mode = cfg["mode"]
            run_id = cfg["run_id"]

            candidate_dir = self.scratch_dir / run_id
            if candidate_dir.exists():
                import shutil
                shutil.rmtree(candidate_dir)
            candidate_dir.mkdir(parents=True, exist_ok=True)

            print(f"--> [RUN {run_id}] Synthesizing candidate: {system_name} (Trial {trial})")
            axioma_kv.generate_candidate_app(mode, candidate_dir)

            print(f"    Evaluating via MacroEvaluationGauntlet...")
            sc = self.gauntlet.evaluate_app(candidate_dir, archetype, mode)
            scorecards.append(sc)

            summary_by_system[system_name]["runs"] += 1
            summary_by_system[system_name]["scores"].append(sc.composite_score)
            if sc.tier0_liveness.passed:
                summary_by_system[system_name]["liveness_passes"] += 1

            status_str = "PASS (1.0x)" if sc.tier0_liveness.passed else "FAIL (0.0x)"
            print(f"    Tier 0 Liveness: {status_str} | Startup: {sc.tier0_liveness.startup_time_ms:.1f}ms")
            print(f"    Composite Quality Score: {sc.composite_score:.1f} / 100.0 (Graded: {sc.graded_score:.1f})\n")

        for sname, data in summary_by_system.items():
            scs = data["scores"]
            data["mean_score"] = round(sum(scs) / len(scs), 2) if scs else 0.0
            data["min_score"] = min(scs) if scs else 0.0
            data["max_score"] = max(scs) if scs else 0.0

        report = Stage1PilotReport(
            report_id=report_id,
            timestamp=time.time(),
            merkle_root=merkle_root,
            total_runs=len(scorecards),
            scorecards=scorecards,
            summary_by_system=summary_by_system,
        )

        # Emit JSON ledger
        ledger_file = self.reports_dir / "stage1_pilot_ledger.json"
        ledger_file.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        print(f"[OK] Emitted sealed ledger to: {ledger_file}")

        # Emit HTML dashboard
        dashboard_file = self.reports_dir / "stage1_pilot_dashboard.html"
        self._generate_dashboard_html(report, dashboard_file)
        print(f"[OK] Emitted visual dashboard to: {dashboard_file}")

        return report

    def _generate_dashboard_html(self, report: Stage1PilotReport, output_file: Path) -> None:
        cards_html = []
        for sc in report.scorecards:
            liveness_badge = (
                '<span class="badge pass">LIVENESS PASS (1.0x)</span>'
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
                            <tr><th>Evaluation Pass</th><th>Weight</th><th>Raw Score</th><th>Weighted</th><th>Status</th></tr>
                        </thead>
                        <tbody>
                            {''.join(passes_rows)}
                        </tbody>
                    </table>
                </div>
            """)

        summary_rows = []
        for sname, data in report.summary_by_system.items():
            summary_rows.append(f"""
                <tr>
                    <td><strong>{sname}</strong></td>
                    <td>{data['runs']}</td>
                    <td>{data['liveness_passes']} / {data['runs']}</td>
                    <td><strong>{data['mean_score']:.1f}</strong></td>
                    <td>{data['min_score']:.1f} – {data['max_score']:.1f}</td>
                </tr>
            """)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Axioma Benchmarking Week: Stage 1 Pilot Dashboard</title>
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
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
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
        .summary-table, .pass-table {{
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
            margin-top: 16px;
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
        <h1>Axioma Benchmarking Week: Stage 1 Pilot Dashboard</h1>
        <p>Report ID: <code>{report.report_id}</code> | Merkle Root: <code>{report.merkle_root[:32]}...</code></p>
    </div>

    <h2>1. Executive Summary: Meta-Axioma vs. Antigravity Vanilla (Axioma-KV)</h2>
    <table class="summary-table">
        <thead>
            <tr>
                <th>System</th>
                <th>Total Runs</th>
                <th>Tier 0 Liveness Passed</th>
                <th>Mean Composite Score</th>
                <th>Score Range</th>
            </tr>
        </thead>
        <tbody>
            {''.join(summary_rows)}
        </tbody>
    </table>

    <h2>2. Individual Run Scorecards & Pass Decompositions</h2>
    {''.join(cards_html)}
</body>
</html>
"""
        output_file.write_text(html_content, encoding="utf-8")


def main() -> None:
    runner = Stage1PilotRunner()
    report = runner.run_pilot()

    print("\n========================================================")
    print("  STAGE 1 PILOT BENCHMARK RESULTS SUMMARY")
    print("========================================================")
    for sname, data in report.summary_by_system.items():
        print(f"- {sname}: Mean Composite Score = {data['mean_score']:.1f} / 100.0 | Liveness = {data['liveness_passes']}/{data['runs']}")
    print("========================================================\n")


if __name__ == "__main__":
    main()
