"""Background Server Daemon Runner for Axioma Crossword (Gen 2)."""

import sys
from pathlib import Path

# Add app dir to sys.path
APP_DIR = Path(__file__).parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from server import run_server

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8094
    run_server(port)
