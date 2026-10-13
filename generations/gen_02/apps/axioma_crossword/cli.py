"""Command-Line Interface for Axioma Crossword (Gen 2) [L1-G2-001].

Provides offline cruciverbalist solving, clue inspection, and grid synthesis.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from .core import TEMPLATE_7X7_QUICK, TEMPLATE_9X9_MIDI, TEMPLATE_11X11_MAXI, CrosswordCspEngine
    from .lexicon import GLOBAL_LEXICON
    from .server import GLOBAL_STORE, run_server
except ImportError:
    from core import TEMPLATE_7X7_QUICK, TEMPLATE_9X9_MIDI, TEMPLATE_11X11_MAXI, CrosswordCspEngine
    from lexicon import GLOBAL_LEXICON
    from server import GLOBAL_STORE, run_server


def cmd_list(args) -> None:
    puzzles = GLOBAL_STORE.list_puzzles()
    print("\nAvailable Crossword Puzzles (Generation 2):")
    for p in puzzles:
        print(f"  [{p['grid_id']}] {p['title']} ({p['size_rows']}x{p['size_cols']}, {p['clues_count']} clues)")
    print()


def cmd_clues(args) -> None:
    puz = GLOBAL_STORE.get_puzzle(args.puzzle_id)
    if not puz:
        print(f"Error: Puzzle '{args.puzzle_id}' not found.")
        sys.exit(1)
    print(f"\nClues for {puz.title}:")
    print("\n--- ACROSS ---")
    for c in puz.clues:
        if c.direction.value == "ACROSS":
            print(f"  {c.number}. {c.surface_text} [{c.clue_type.value}]")
    print("\n--- DOWN ---")
    for c in puz.clues:
        if c.direction.value == "DOWN":
            print(f"  {c.number}. {c.surface_text} [{c.clue_type.value}]")
    print()


def cmd_serve(args) -> None:
    run_server(args.port)


def main() -> None:
    parser = argparse.ArgumentParser(description="Axioma Crossword CLI (Gen 2)")
    subparsers = parser.add_subparsers(dest="command")

    # list
    p_list = subparsers.add_parser("list", help="List available puzzles")
    p_list.set_defaults(func=cmd_list)

    # clues
    p_clues = subparsers.add_parser("clues", help="Inspect clues for a puzzle")
    p_clues.add_argument("puzzle_id", default="puzzle_quick_01", nargs="?")
    p_clues.set_defaults(func=cmd_clues)

    # serve
    p_serve = subparsers.add_parser("serve", help="Run the Web Studio HTTP daemon")
    p_serve.add_argument("--port", type=int, default=8094)
    p_serve.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
