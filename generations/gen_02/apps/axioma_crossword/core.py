"""Constraint Satisfaction Problem (CSP) Engine for Crossword Grid Synthesis.

Implements Backtracking with AC-3 / Forward Checking and Minimum Remaining Values (MRV).
Employs Landauer Accounting ([L1-008]) to measure information erasure and dissipated heat,
and enforces strict execution leases to prevent event-loop thread starvation ([L1-015_1]).
"""

from __future__ import annotations

import math
import time
from typing import Callable, Dict, List, Optional, Set, Tuple

try:
    from .lexicon import GLOBAL_LEXICON, CrypticLexicon
    from .models import (
        CrosswordGrid,
        CrypticClue,
        Direction,
        LandauerSearchAudit,
        WordSlot,
    )
except ImportError:
    from lexicon import GLOBAL_LEXICON, CrypticLexicon
    from models import (
        CrosswordGrid,
        CrypticClue,
        Direction,
        LandauerSearchAudit,
        WordSlot,
    )

# Boltzmann constant in J/K
KB = 1.380649e-23
ROOM_TEMP_K = 300.0
LN2 = math.log(2.0)


class LandauerBudgetExceededError(RuntimeError):
    """Raised when search exceeds allocated Landauer entropy or backtrack lease."""
    pass


class CrosswordCspEngine:
    """Rigorous CSP Solver for 2D Crossword Grids."""

    def __init__(self, lexicon: Optional[CrypticLexicon] = None):
        self.lexicon = lexicon or GLOBAL_LEXICON

    @staticmethod
    def extract_slots(cells: List[List[str]]) -> List[WordSlot]:
        """Extracts Across and Down WordSlots and assigns standard cruciverbalist numbers."""
        rows = len(cells)
        cols = len(cells[0])
        slots: List[WordSlot] = []

        current_number = 1

        for r in range(rows):
            for c in range(cols):
                if cells[r][c] == "#":
                    continue

                is_across_start = (c == 0 or cells[r][c - 1] == "#") and (c + 1 < cols and cells[r][c + 1] != "#")
                is_down_start = (r == 0 or cells[r - 1][c] == "#") and (r + 1 < rows and cells[r + 1][c] != "#")

                assigned_num = False

                if is_across_start:
                    length = 0
                    while c + length < cols and cells[r][c + length] != "#":
                        length += 1
                    slot_id = f"A_{r}_{c}"
                    slots.append(
                        WordSlot(
                            slot_id=slot_id,
                            direction=Direction.ACROSS,
                            row=r,
                            col=c,
                            length=length,
                            number=current_number,
                            answer="",
                        )
                    )
                    assigned_num = True

                if is_down_start:
                    length = 0
                    while r + length < rows and cells[r + length][c] != "#":
                        length += 1
                    slot_id = f"D_{r}_{c}"
                    slots.append(
                        WordSlot(
                            slot_id=slot_id,
                            direction=Direction.DOWN,
                            row=r,
                            col=c,
                            length=length,
                            number=current_number,
                            answer="",
                        )
                    )
                    assigned_num = True

                if assigned_num:
                    current_number += 1

        return slots

    @staticmethod
    def compute_intersections(
        slots: List[WordSlot],
    ) -> Dict[Tuple[str, str], Tuple[int, int]]:
        """Maps pairs of intersecting slots to (idx_in_slot1, idx_in_slot2)."""
        intersections: Dict[Tuple[str, str], Tuple[int, int]] = {}

        # Organize by coordinates
        across_cells: Dict[Tuple[int, int], Tuple[WordSlot, int]] = {}
        down_cells: Dict[Tuple[int, int], Tuple[WordSlot, int]] = {}

        for slot in slots:
            if slot.direction == Direction.ACROSS:
                for offset in range(slot.length):
                    across_cells[(slot.row, slot.col + offset)] = (slot, offset)
            else:
                for offset in range(slot.length):
                    down_cells[(slot.row + offset, slot.col)] = (slot, offset)

        for coord, (a_slot, a_idx) in across_cells.items():
            if coord in down_cells:
                d_slot, d_idx = down_cells[coord]
                intersections[(a_slot.slot_id, d_slot.slot_id)] = (a_idx, d_idx)
                intersections[(d_slot.slot_id, a_slot.slot_id)] = (d_idx, a_idx)

        return intersections

    def solve_grid(
        self,
        slots: List[WordSlot],
        intersections: Dict[Tuple[str, str], Tuple[int, int]],
        max_backtracks: int = 4000,
        max_seconds: float = 5.0,
        progress_callback: Optional[Callable[[int, int, float], None]] = None,
    ) -> Tuple[Dict[str, str], LandauerSearchAudit]:
        """Solves the grid CSP using Backtracking with MRV, Forward Checking, and Landauer tracking."""
        start_time = time.time()
        backtracks_count = 0
        pruned_candidates_count = 0
        total_erased_bits = 0.0

        # Initial domains for each slot, prioritizing curated words with authentic clues
        domains: Dict[str, List[str]] = {}
        curated_answers = getattr(self.lexicon, "curated_answers", set())
        for slot in slots:
            words = self.lexicon.get_words_of_length(slot.length)
            if not words:
                raise ValueError(f"No dictionary words available for slot {slot.slot_id} of length {slot.length}")
            # Prioritize curated answers (0) over procedural ones (1)
            sorted_words = sorted(words, key=lambda w: (0 if w in curated_answers else 1))
            domains[slot.slot_id] = sorted_words

        neighbors: Dict[str, List[Tuple[str, int, int]]] = collections_neighbors(slots, intersections)

        assignment: Dict[str, str] = {}
        used_words: Set[str] = set()

        def backtrack(current_domains: Dict[str, List[str]]) -> Optional[Dict[str, str]]:
            nonlocal backtracks_count, pruned_candidates_count, total_erased_bits

            # Check time lease
            if time.time() - start_time > max_seconds:
                raise LandauerBudgetExceededError(f"Search timed out after {max_seconds:.2f}s")

            # Check backtrack quota
            if backtracks_count > max_backtracks:
                raise LandauerBudgetExceededError(f"Search exceeded Landauer backtrack quota ({max_backtracks} steps)")

            if len(assignment) == len(slots):
                return assignment

            # Minimum Remaining Values (MRV) heuristic: select unassigned slot with smallest domain
            unassigned = [s.slot_id for s in slots if s.slot_id not in assignment]
            unassigned.sort(key=lambda s_id: len(current_domains[s_id]))
            chosen_slot_id = unassigned[0]
            candidates = [w for w in current_domains[chosen_slot_id] if w not in used_words]

            if not candidates:
                return None

            for word in candidates:
                # Tentative assignment
                assignment[chosen_slot_id] = word
                used_words.add(word)

                # Forward Checking: prune incompatible words in neighbor domains
                new_domains = {k: list(v) for k, v in current_domains.items()}
                new_domains[chosen_slot_id] = [word]

                conflict = False
                pruned_this_step = 0

                for n_id, my_idx, n_idx in neighbors.get(chosen_slot_id, []):
                    if n_id in assignment:
                        continue

                    required_char = word[my_idx]
                    valid_n_words = [
                        w for w in new_domains[n_id] if w[n_idx] == required_char and w not in used_words
                    ]
                    pruned_this_step += (len(new_domains[n_id]) - len(valid_n_words))
                    new_domains[n_id] = valid_n_words

                    if not valid_n_words:
                        conflict = True
                        break

                pruned_candidates_count += pruned_this_step

                if not conflict:
                    if progress_callback and backtracks_count % 50 == 0:
                        joules = total_erased_bits * KB * ROOM_TEMP_K * LN2
                        progress_callback(backtracks_count, pruned_candidates_count, joules)

                    result = backtrack(new_domains)
                    if result is not None:
                        return result

                # Backtrack & erase information (Landauer erasure)
                del assignment[chosen_slot_id]
                used_words.remove(word)
                backtracks_count += 1
                erased_bits = math.log2(max(1, len(candidates)))
                total_erased_bits += erased_bits

            return None

        solution = backtrack(domains)
        if not solution:
            raise ValueError("No consistent crossword solution found within the given dictionary constraints.")

        joules_dissipated = total_erased_bits * KB * ROOM_TEMP_K * LN2
        pruned_ratio = (
            pruned_candidates_count / max(1, pruned_candidates_count + backtracks_count)
        )

        audit = LandauerSearchAudit(
            search_id=f"audit_{int(start_time)}",
            total_backtracks=backtracks_count,
            candidate_domain_erased_bits=round(total_erased_bits, 2),
            joules_dissipated=joules_dissipated,
            pruned_branches_ratio=round(pruned_ratio, 4),
        )

        return solution, audit

    def generate_puzzle(
        self,
        grid_id: str,
        title: str,
        grid_template: List[List[str]],
        max_backtracks: int = 4000,
    ) -> CrosswordGrid:
        """Synthesizes a full CrosswordGrid with verifiable cryptic clue ASTs."""
        slots = self.extract_slots(grid_template)
        intersections = self.compute_intersections(slots)

        solution, audit = self.solve_grid(slots, intersections, max_backtracks=max_backtracks)
        self.last_audit = audit

        # Build filled slots
        solved_slots = []
        clues: List[CrypticClue] = []

        for slot in slots:
            answer = solution[slot.slot_id]
            solved_slot = WordSlot(
                slot_id=slot.slot_id,
                direction=slot.direction,
                row=slot.row,
                col=slot.col,
                length=slot.length,
                number=slot.number,
                answer=answer,
            )
            solved_slots.append(solved_slot)

            clue = self.lexicon.get_clue_for_word(
                word=answer,
                clue_id=f"clue_{slot.slot_id}",
                slot_id=slot.slot_id,
                number=slot.number,
                direction=slot.direction,
            )
            clues.append(clue)

        # Generate filled cells
        rows = len(grid_template)
        cols = len(grid_template[0])
        filled_cells = [list(row) for row in grid_template]

        for slot in solved_slots:
            if slot.direction == Direction.ACROSS:
                for idx, ch in enumerate(slot.answer):
                    filled_cells[slot.row][slot.col + idx] = ch
            else:
                for idx, ch in enumerate(slot.answer):
                    filled_cells[slot.row + idx][slot.col] = ch

        return CrosswordGrid(
            grid_id=grid_id,
            title=title,
            size_rows=rows,
            size_cols=cols,
            cells=filled_cells,
            slots=solved_slots,
            clues=clues,
            symmetry="ROTATIONAL_180",
        )


def collections_neighbors(
    slots: List[WordSlot], intersections: Dict[Tuple[str, str], Tuple[int, int]]
) -> Dict[str, List[Tuple[str, int, int]]]:
    """Helper to organize intersections by slot."""
    neighbors: Dict[str, List[Tuple[str, int, int]]] = {}
    for slot in slots:
        neighbors[slot.slot_id] = []

    for (s1, s2), (idx1, idx2) in intersections.items():
        if s1 in neighbors:
            neighbors[s1].append((s2, idx1, idx2))
    return neighbors


# Pre-defined Symmetric Grid Templates
TEMPLATE_7X7_QUICK = [
    ["", "", "", "#", "", "", ""],
    ["", "#", "", "#", "", "#", ""],
    ["", "", "", "", "", "", ""],
    ["#", "#", "", "#", "", "#", "#"],
    ["", "", "", "", "", "", ""],
    ["", "#", "", "#", "", "#", ""],
    ["", "", "", "#", "", "", ""],
]

TEMPLATE_9X9_MIDI = [
    ["", "", "", "", "", "#", "", "", ""],
    ["", "#", "", "#", "", "#", "", "#", ""],
    ["", "", "", "", "", "", "", "", ""],
    ["", "#", "", "#", "", "#", "", "#", ""],
    ["#", "", "", "", "", "", "", "", "#"],
    ["", "#", "", "#", "", "#", "", "#", ""],
    ["", "", "", "", "", "", "", "", ""],
    ["", "#", "", "#", "", "#", "", "#", ""],
    ["", "", "", "#", "", "", "", "", ""],
]

TEMPLATE_11X11_MAXI = [
    ["", "", "", "", "", "#", "", "", "", "", ""],
    ["", "#", "", "#", "", "#", "", "#", "", "#", ""],
    ["", "", "", "", "", "", "", "", "", "", ""],
    ["", "#", "", "#", "", "#", "", "#", "", "#", ""],
    ["", "", "", "", "#", "", "", "", "", "", ""],
    ["#", "#", "", "#", "", "#", "", "#", "", "#", "#"],
    ["", "", "", "", "", "", "#", "", "", "", ""],
    ["", "#", "", "#", "", "#", "", "#", "", "#", ""],
    ["", "", "", "", "", "", "", "", "", "", ""],
    ["", "#", "", "#", "", "#", "", "#", "", "#", ""],
    ["", "", "", "", "", "#", "", "", "", "", ""],
]

