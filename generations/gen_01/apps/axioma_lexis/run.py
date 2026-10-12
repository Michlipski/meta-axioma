#!/usr/bin/env python3
"""Executable launcher for Axioma Lexis."""
from pathlib import Path
import sys

app_root = Path(__file__).parent
sys.path.insert(0, str(app_root / "src"))

from server import run_server

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    run_server(port=port)
