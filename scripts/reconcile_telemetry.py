#!/usr/bin/env python3
"""Canonical Telemetry Reconciler & Dashboard Compiler Invoker ([L1-G4B-008]).

Extracts empirical token measurements and compiles hermetic HTML5 dashboards
using TelemetryDashboardCompiler in <50ms without sandbox elevation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from generations.gen_04b.services.telemetry.src.dashboard_compiler import (
    TelemetryDashboardCompiler,
)

ALL_TARGETS = [
    "generations/gen_04b/apps/axioma_canvas",
    "generations/gen_04b/apps/axioma_consensus",
    "generations/gen_04b/apps/axioma_crucible",
    "generations/gen_04b/apps/axioma_go",
    "generations/gen_04b/apps/axioma_phenoflora",
    "generations/gen_04b/services/audit",
    "generations/gen_04b/services/builder",
    "generations/gen_04b/services/governance",
    "generations/gen_04b/services/telemetry",
]


def reconcile_and_compile(target_path: Path) -> tuple[Path, Path]:
    """Compiles hermetic dashboard deliverables for a target directory."""
    t0 = time.perf_counter()
    p1, p2 = TelemetryDashboardCompiler.compile_and_save(target_path)
    t_ms = (time.perf_counter() - t0) * 1000
    size_kb = p1.stat().st_size / 1024
    print(f"[{target_path.name}] Emitted: {p1.name} & {p2.name} ({size_kb:.1f} KB in {t_ms:.2f}ms)")
    return p1, p2


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconcile and compile telemetry dashboards")
    parser.add_argument("--app", type=str, help="Target application or service name/path")
    parser.add_argument("--all", action="store_true", help="Reconcile all 9 Generation 4b targets")
    args = parser.parse_args()

    targets: list[Path] = []
    if args.all or not args.app:
        targets = [repo_root / t for t in ALL_TARGETS if (repo_root / t).exists()]
    else:
        cand = Path(args.app)
        if not cand.is_absolute():
            for base in ["generations/gen_04b/apps", "generations/gen_04b/services", "apps"]:
                if (repo_root / base / args.app).exists():
                    cand = repo_root / base / args.app
                    break
            else:
                cand = repo_root / args.app
        if not cand.exists():
            print(f"Error: Target '{args.app}' not found.", file=sys.stderr)
            sys.exit(1)
        targets = [cand]

    for t in targets:
        reconcile_and_compile(t)


if __name__ == "__main__":
    main()
