#!/usr/bin/env python3
"""Application Launcher for Axioma Flow (Compiled by System G_1)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from server import run_server

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8088
    run_server(port=port)
