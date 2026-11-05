#!/usr/bin/env python3
"""Meta-Axioma Presentation Demo Fleet Launcher (`launch_demo_fleet.py`).

Boots all interactive Gen 4b demonstration apps and the Telemetry Cockpit
concurrently in supervised subprocesses, providing a single unified HUD of
clickable URLs for the live presentation.

Applications:
  1. Telemetry Cockpit & Mesh:    http://localhost:8447/ (or http://192.168.40.40:8447/)
  2. Axioma Go (Tactile Game):    http://localhost:8082/
  3. Axioma Consensus (RFC Bus):  http://localhost:8083/
  4. Axioma Canvas (Studio HUD):  http://localhost:8084/
  5. Axioma Crucible (AST/Quine): http://localhost:8085/
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

REPO_ROOT = Path(__file__).resolve().parent.parent

# ANSI Colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
PURPLE = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

APP_SPECS = [
    {
        "id": "telemetry_mesh",
        "name": "Sovereign Service Mesh & Cockpit",
        "cmd": [sys.executable, str(REPO_ROOT / "scripts" / "run_sovereign_mesh.py"), "--mode", "auto"],
        "url": "http://localhost:8447/",
        "desc": "Real-time SSE event stream, WAL transaction scrubber, live node graph",
    },
    {
        "id": "axioma_go",
        "name": "Axioma Go (10x10 Board Game)",
        "cmd": [sys.executable, str(REPO_ROOT / "generations" / "gen_04b" / "apps" / "axioma_go" / "run.py"), "--port", "8082"],
        "url": "http://localhost:8082/",
        "desc": "Interactive Go captures (Snapback, Ladder, Crane's Nest, Double Atari)",
    },
    {
        "id": "axioma_consensus",
        "name": "Axioma Consensus (CRDT & RFC HUD)",
        "cmd": [sys.executable, str(REPO_ROOT / "generations" / "gen_04b" / "apps" / "axioma_consensus" / "run.py"), "--port", "8083"],
        "url": "http://localhost:8083/",
        "desc": "Leaderless CRDT semilattices & 2-of-3 Sheaf-Quorum consensus cockpit",
    },
    {
        "id": "axioma_canvas",
        "name": "Axioma Canvas (Statechart Studio)",
        "cmd": [sys.executable, str(REPO_ROOT / "generations" / "gen_04b" / "apps" / "axioma_canvas" / "run.py"), "--port", "8084", "--demo"],
        "url": "http://localhost:8084/",
        "desc": "Visual tactile reactive studio & state machine authoring cockpit",
    },
    {
        "id": "axioma_crucible",
        "name": "Axioma Crucible (AST Quine Studio)",
        "cmd": [sys.executable, str(REPO_ROOT / "generations" / "gen_04b" / "apps" / "axioma_crucible" / "run.py")],
        "url": "http://localhost:8085/",
        "desc": "AST skeletonization, byte-indexed diagnostic tuples & Quine verification",
    },
]


def main():
    parser = argparse.ArgumentParser(description="Meta-Axioma Demo Fleet Launcher")
    parser.add_argument("--only", nargs="+", help="Specific apps to launch (e.g. telemetry_mesh axioma_go)")
    args = parser.parse_args()

    selected = APP_SPECS
    if args.only:
        selected = [s for s in APP_SPECS if s["id"] in args.only]

    print("\n" + "=" * 80)
    print(f"{BOLD}{CYAN}META-AXIOMA: LIVE PRESENTATION DEMO FLEET LAUNCHER{RESET}")
    print("=" * 80)
    print(f"Launching {len(selected)} interactive demonstration endpoints...\n")

    processes: list[tuple[dict, subprocess.Popen]] = []

    try:
        for spec in selected:
            p = subprocess.Popen(
                spec["cmd"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(REPO_ROOT),
                preexec_fn=os.setsid if hasattr(os, "setsid") else None,
            )
            processes.append((spec, p))
            print(f"  {GREEN}▶{RESET} {BOLD}{spec['name']:<35}{RESET} -> {CYAN}{spec['url']}{RESET}")
            time.sleep(0.3)

        print("\n" + "=" * 80)
        print(f"{BOLD}ALL DEMO APPS RUNNING. CLICK LINKS BELOW TO PRESENT:{RESET}")
        print("=" * 80)
        for spec, _ in processes:
            print(f"  {BOLD}{spec['name']}{RESET}")
            print(f"    URL:         {CYAN}{spec['url']}{RESET}")
            print(f"    Description: {spec['desc']}\n")

        print("=" * 80)
        print(f"{YELLOW}Press Ctrl+C to terminate all demo servers cleanly.{RESET}\n")

        while True:
            time.sleep(1)
            # Check if any child process died
            for spec, p in processes:
                if p.poll() is not None:
                    print(f"  {RED}[WARNING] Process '{spec['name']}' exited with code {p.returncode}{RESET}")

    except KeyboardInterrupt:
        print("\n\nShutting down demo fleet...")
        for spec, p in processes:
            try:
                if hasattr(os, "killpg"):
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                else:
                    p.terminate()
            except Exception:
                pass
        time.sleep(0.5)
        print(f"{GREEN}All demo apps cleanly terminated.{RESET}\n")


if __name__ == "__main__":
    main()
