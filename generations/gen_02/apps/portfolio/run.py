#!/usr/bin/env python3
"""Standardized launcher for Michael Lipski Portfolio website.

Serves the statically compiled Next.js export bundle from out/ on http://localhost:3000.
"""

import http.server
import os
import socketserver
import sys
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 3000))
BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "out"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(OUT_DIR), **kwargs)

    def log_message(self, format, *args):
        # Keep logs clean
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

def main():
    if not OUT_DIR.exists():
        print(f"Error: {OUT_DIR} does not exist. Run 'npm run build' first.")
        sys.exit(1)

    # Enable socket address reuse to prevent port-in-use faults on restart
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("=" * 60)
        print("  Michael Lipski — Engineering Portfolio Live Server")
        print(f"  Serving static bundle from: {OUT_DIR}")
        print(f"  URL: http://localhost:{PORT}")
        print("=" * 60)
        print("Press Ctrl+C to terminate.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    main()
