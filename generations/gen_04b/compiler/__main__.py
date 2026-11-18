"""Module entrypoint for `python3 -m generations.gen_04b.compiler`."""

from __future__ import annotations

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
