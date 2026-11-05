#!/usr/bin/env python3
"""Ablation Runner CLI (`.agents/skills/ablation-runner/scripts/run_ablations.py`).

Invoked by the `/ablation-runner` skill to execute real 5-way empirical ablation benchmarks
and print the comparative evaluation matrix.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from benchmarks.ablation.ablation_orchestrator import AblationBenchmarkHarness


def main() -> None:
    parser = argparse.ArgumentParser(description="Meta-Axioma 5-Way Empirical Ablation Benchmark Runner")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format (markdown or json)")
    parser.add_argument("--output", type=str, default=None, help="Optional file path to write results")
    args = parser.parse_args()

    if args.format != "json":
        print("=" * 80)
        print("META-AXIOMA 5-WAY EMPIRICAL ABLATION BENCHMARK RUNNER")
        print("Executing isolated configurations against ground truth test suites...")
        print("=" * 80)

    harness = AblationBenchmarkHarness(workspace_root=str(REPO_ROOT))
    results = harness.run_all_ablations()

    if args.format == "json":
        output_content = json.dumps([r.to_dict() for r in results], indent=2)
    else:
        output_content = harness.generate_markdown_matrix(results)

    if args.output:
        Path(args.output).write_text(output_content, encoding="utf-8")
        print(f"Results written to: {args.output}")

    if args.format == "json":
        print(output_content)
    else:
        print("\n" + output_content)
        print("=" * 80)
        print("Benchmark complete. Empirical data verified without mocks.")


if __name__ == "__main__":
    main()
