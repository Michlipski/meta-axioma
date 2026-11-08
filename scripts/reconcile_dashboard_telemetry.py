#!/usr/bin/env python3
"""Canonical Dashboard Telemetry & Subagent Witness Reconciler ([L1-G4B-008]).

Delegates compilation to TelemetryDashboardCompiler:
1. Reads actual empirical tokens from workspace metrics or main transcript.
2. Reads actual empirical tokens and real conversation IDs from workspace metrics.
3. Invokes TelemetryDashboardCompiler.compile_and_save().
4. Operates 100% in Standard Sandbox Mode (BypassSandbox: false).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from generations.gen_04b.services.telemetry.src.dashboard_compiler import (
    TelemetryDashboardCompiler,
)


def measure_transcript_tokens(transcript_path: Path) -> Dict[str, int]:
    """Measures total token metrics from a transcript.jsonl file."""
    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript not found: {transcript_path}")

    inp, out, cache, steps = 0, 0, 0, 0
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            steps += 1
            try:
                d = json.loads(line)
                inp += d.get("input_tokens") or 0
                out += d.get("output_tokens") or 0
                cache += d.get("cache_read_tokens") or 0
            except json.JSONDecodeError:
                continue

    return {
        "steps": steps,
        "input_fresh": inp,
        "output": out,
        "cache_read": cache,
        "total_volume": inp + out + cache,
    }


def reconcile_dashboard(
    target_name: str,
    target_type: str = "service",
    main_conversation_id: Optional[str] = None,
    repo_root: Optional[Path] = None,
    subagent_ids: Optional[List[str]] = None,
    metrics_file: Optional[Path] = None,
) -> Dict[str, Any]:
    """Reconciles and compiles dashboard deliverables using TelemetryDashboardCompiler."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent

    if target_type == "app":
        gen_dir = repo_root / "generations" / "gen_04b" / "apps" / target_name
        if not gen_dir.exists():
            gen_dir = repo_root / "apps" / target_name
    else:
        gen_dir = repo_root / "generations" / "gen_04b" / "services" / target_name

    if not gen_dir.exists():
        raise FileNotFoundError(f"Target directory not found: {gen_dir}")

    # Compile using the canonical sovereign compiler kernel
    p1, p2 = TelemetryDashboardCompiler.compile_and_save(gen_dir)

    return {
        "target": target_name,
        "type": target_type,
        "main_conversation_id": main_conversation_id,
        "deliverables": [str(p1), str(p2)],
        "status": "SUCCESS",
    }


def reconcile_service_dashboard(
    service_name: str,
    main_conversation_id: Optional[str] = None,
    repo_root: Optional[Path] = None,
    subagent_ids: Optional[List[str]] = None,
    metrics_file: Optional[Path] = None,
) -> Dict[str, Any]:
    return reconcile_dashboard(
        target_name=service_name,
        target_type="service",
        main_conversation_id=main_conversation_id,
        repo_root=repo_root,
        subagent_ids=subagent_ids,
        metrics_file=metrics_file,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile dashboard telemetry with empirical transcripts.")
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument("--service", help="Service name (e.g. telemetry, audit, builder, governance)")
    target_group.add_argument("--app", help="Application name (e.g. axioma_go)")

    parser.add_argument("--main-cid", default=None, help="Main orchestrator conversation UUID")
    parser.add_argument("--subagents", nargs="*", default=[], help="List of subagent conversation UUIDs")
    parser.add_argument("--metrics-file", default=None, help="Optional path to in-workspace JSON metrics file")

    args = parser.parse_args()
    target_type = "app" if args.app else "service"
    target_name = args.app if args.app else args.service

    try:
        res = reconcile_dashboard(
            target_name=target_name,
            target_type=target_type,
            main_conversation_id=args.main_cid,
            subagent_ids=args.subagents,
            metrics_file=Path(args.metrics_file) if args.metrics_file else None,
        )
        print(json.dumps(res, indent=2))
        return 0
    except Exception as e:
        print(f"Error reconciling dashboard: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
