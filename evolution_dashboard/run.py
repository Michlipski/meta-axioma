#!/usr/bin/env python3
"""
Launcher for Axioma Evolution Dashboard (Root Level, Port 8105).
Supports:
  python3 run.py [--port 8105] [--host 0.0.0.0] [--verify-only]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from src.data_store import EvolutionDataStore
from server import run_server


def verify_dataset() -> bool:
    print("[1/4] Verifying Evolution Dataset & G4b Schemas...")
    store = EvolutionDataStore()
    health = store.get_health()
    print(f"  [OK] Stages Count: {health['stages_count']} (S0 -> G4b)")
    print(f"  [OK] Transformations Count: {health['transformations_count']}")
    print(f"  [OK] Subsystems Count: {health['subsystems_count']}")

    print("\n[2/4] Verifying Philosophy & G4b Sovereign Mesh...")
    phil = store.get_philosophy()
    if not phil or "surface_layman" not in phil:
        print("  [FAIL] Philosophy dataset missing or invalid!", file=sys.stderr)
        return False
    print("  [OK] Philosophy dataset verified (Layman pillars + Jettison milestones)")

    g4b = store.get_g4b_architecture()
    if not g4b or len(g4b.get("services", [])) != 5:
        print("  [FAIL] G4b Sovereign Services count mismatch!", file=sys.stderr)
        return False
    print("  [OK] G4b 5 Sovereign Services verified (Research, Builder, Audit, Telemetry, Governance)")

    print("\n[3/4] Verifying Sample App Compilation Simulations & Thermodynamics...")
    sims = store.get_simulations()
    expected_apps = ["axioma_go", "axioma_flow", "axioma_sentinel"]
    for app in expected_apps:
        app_sim = store.get_simulation(app)
        if not app_sim or len(app_sim.get("steps", [])) < 3:
            print(f"  [FAIL] Simulation missing or invalid for app '{app}'!", file=sys.stderr)
            return False
    print(f"  [OK] Sample app simulations verified ({', '.join(expected_apps)})")

    # Landauer thermodynamic dissipation verification [L1-008]
    heat = store.calculate_landauer_heat(1000000, 300.0)
    if heat <= 0:
        print("  [FAIL] Landauer heat dissipation must be strictly positive!", file=sys.stderr)
        return False
    print(f"  [OK] Landauer heat dissipation verified (1M bits @ 300K = {heat:.4e} J)")

    print("\n[4/4] Verifying Cross-Schema Generational Diff Engine (Dict vs String Invariants)...")
    # Diff S0 -> G4b
    diff_s0_g4b = store.get_generational_diff("s0", "g4b")
    if "stage_a" not in diff_s0_g4b or "stage_b" not in diff_s0_g4b:
        print("  [FAIL] Generational diff engine error on s0 -> g4b!", file=sys.stderr)
        return False
    if "L1-002" not in diff_s0_g4b.get("invariants_retained", []):
        print("  [FAIL] L1-002 expected to be retained between s0 and g4b!", file=sys.stderr)
        return False
    print("  [OK] S0 -> G4b diff verified (Functorial undo morphism L1-002 retained)")

    # Diff G3b -> G4b (Dict schema vs String schema cross-reconciliation)
    diff_g3b_g4b = store.get_generational_diff("g3b", "g4b")
    retained_g3b_g4b = diff_g3b_g4b.get("invariants_retained", [])
    expected_retained = ["L1-G3B-000", "L1-G3B-011", "L1-G3B-012", "L1-G3B-014", "L1-G3B-017", "L1-G3B-018"]
    for inv in expected_retained:
        if inv not in retained_g3b_g4b:
            print(f"  [FAIL] Expected retained invariant {inv} missing in G3b->G4b diff!", file=sys.stderr)
            return False
    print(f"  [OK] G3b -> G4b cross-schema diff verified ({len(retained_g3b_g4b)} invariants preserved)")

    # Verify all 8 stages can be pairwise diffed
    stages = [s["id"] for s in store.get_stages()]
    for i in range(len(stages) - 1):
        pair_diff = store.get_generational_diff(stages[i], stages[i + 1])
        if not pair_diff or "stage_a" not in pair_diff or "stage_b" not in pair_diff:
            print(f"  [FAIL] Pairwise diff failed for {stages[i]} -> {stages[i+1]}!", file=sys.stderr)
            return False
    print("  [OK] All 7 consecutive generational transitions pairwise diff verified")

    print("\nAll datasets and structural invariants verified successfully!")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Axioma Evolution Dashboard Launcher")
    parser.add_argument("--port", type=int, default=8105, help="Port to listen on (default: 8105)")
    parser.add_argument("--host", default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    parser.add_argument("--verify-only", action="store_true", help="Verify data integrity and exit")
    args = parser.parse_args()

    if args.verify_only:
        success = verify_dataset()
        sys.exit(0 if success else 1)

    if not verify_dataset():
        print("Dataset verification failed. Aborting server launch.", file=sys.stderr)
        sys.exit(1)

    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
