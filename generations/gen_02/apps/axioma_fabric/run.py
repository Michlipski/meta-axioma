#!/usr/bin/env python3
"""Standard entrypoint for Axioma Fabric (SYS-09)."""

import os
import sys

fabric_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(fabric_dir, "src")
cli_dir = os.path.join(fabric_dir, "cli")

sys.path.insert(0, src_dir)
sys.path.insert(0, cli_dir)

from fabric_cli import cmd_serve
import argparse

if __name__ == "__main__":
    port = 8443
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    
    args = argparse.Namespace(
        host="127.0.0.1",
        port=port,
        secret="axioma_secret_dev_key_g2_2026",
    )
    cmd_serve(args)
