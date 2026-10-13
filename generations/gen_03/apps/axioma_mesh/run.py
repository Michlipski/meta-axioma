#!/usr/bin/env python3
"""Standard entrypoint for Axioma Mesh (SYS-09)."""

import sys
from pathlib import Path

mesh_dir = Path(__file__).resolve().parent
g3_src = mesh_dir.parent.parent / "src"
if str(g3_src) not in sys.path:
    sys.path.insert(0, str(g3_src))
if str(mesh_dir) not in sys.path:
    sys.path.insert(0, str(mesh_dir))

from server import run_server

if __name__ == "__main__":
    port = 8200
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port=port)
