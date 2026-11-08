"""CLI Entrypoint for the Sovereign Telemetry Dashboard Compiler ([L1-G4B-008])."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

from .compiler import TelemetryDashboardCompiler

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Meta-Axioma Telemetry Dashboard Compiler")
    parser.add_argument("--app", type=str, help="Path to application or service directory")
    parser.add_argument("--all", action="store_true", help="Compile all 9 Generation 4b apps and services")
    parser.add_argument("--check", action="store_true", help="Validate outputs with ZeroTrustMicroAuditor")

    args = parser.parse_args()

    if not args.app and not args.all:
        parser.print_help()
        sys.exit(1)

    targets = []
    repo_root = Path(__file__).resolve().parents[6]

    if args.all:
        for t in ALL_TARGETS:
            tp = repo_root / t
            if tp.exists():
                targets.append(tp)
    elif args.app:
        ap = Path(args.app).resolve()
        if not ap.exists():
            ap = repo_root / args.app
        if not ap.exists():
            print(f"Error: Target path not found: {args.app}", file=sys.stderr)
            sys.exit(1)
        targets.append(ap)

    print(f"=== Compiling {len(targets)} Telemetry Dashboards ===")
    total_start = time.perf_counter()

    for target in targets:
        t_start = time.perf_counter()
        p1, p2 = TelemetryDashboardCompiler.compile_and_save(target)
        t_ms = (time.perf_counter() - t_start) * 1000
        size_kb = p1.stat().st_size / 1024
        print(f"[{target.name}] Emitted: {p1.name} & {p2.name} ({size_kb:.1f} KB in {t_ms:.2f}ms)")

        if args.check:
            from generations.gen_04b.services.audit.src.zero_trust_micro_auditor import ZeroTrustMicroAuditor
            auditor = ZeroTrustMicroAuditor(f"cli_auditor_{target.name}")
            report = auditor.audit_dashboard_deliverable(p1.read_text(encoding="utf-8"), deliverable_id=p1.name, base_dir=str(target))
            if not report.is_hermetic:
                print(f"  [ERROR] {p1.name} failed hermetic audit:", file=sys.stderr)
                for v in report.violations:
                    print(f"    - [{v.rule_id}] {v.description}", file=sys.stderr)
                sys.exit(1)
            else:
                print("  -> Passed ZeroTrustMicroAuditor HERM-005 & HERM-006")

    total_s = time.perf_counter() - total_start
    print(f"All {len(targets)} dashboards compiled successfully in {total_s:.3f}s.")


if __name__ == "__main__":
    main()
