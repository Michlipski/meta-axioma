#!/usr/bin/env python3
"""Root server entrypoint for Axioma Swarm."""

from pathlib import Path
import sys

app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir / "src"))

from server import run_server

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8098
    run_server(port=port)
