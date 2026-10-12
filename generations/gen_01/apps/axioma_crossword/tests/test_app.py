"""Unit and integration test suite for System 04: Axioma Crossword Engine.

Verifies strict adherence to L1-004 (Universal Grammar Clue AST), L1-015_1 (Compositional Boundary Isolation),
L1-008 (Landauer Thermodynamic Search Accounting), L1-002 (Functorial Reversibility),
and L1-016 (Demarcated Exception Enclaves).
"""

import sys
import time
import unittest
from pathlib import Path

APP_DIR = Path(__file__).parent.parent
SRC_DIR = APP_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from csp_engine import (
    TEMPLATE_7X7_QUICK,
    CrosswordCspEngine,
    LandauerBudgetExceededError,
)
from lexicon import GLOBAL_LEXICON, CrypticLexicon
from models import ClueType, Direction, JobStatus, WordSlot
from server import ExceptionEnclave
from session_store import SessionStore
from worker_pool import CrosswordWorkerPool


class TestAxiomaCrossword(unittest.TestCase):
    """Full verification suite for Axioma Crossword Engine."""

    def test_lexicon_inverted_index_and_candidates(self):
        """Verifies O(1) candidate lookup using positional character inverted index."""
        # 3-letter words starting with 'C'
        candidates_c = GLOBAL_LEXICON.get_candidates(3, {0: "C"})
        self.assertGreaterEqual(len(candidates_c), 5)
        for w in candidates_c:
            self.assertEqual(len(w), 3)
            self.assertEqual(w[0], "C")

        # 3-letter words starting with 'C' and ending with 'T' -> CAT, CUT
        candidates_ct = GLOBAL_LEXICON.get_candidates(3, {0: "C", 2: "T"})
        self.assertIn("CAT", candidates_ct)
        self.assertIn("CUT", candidates_ct)

    def test_cryptic_clue_ast_projection(self):
        """[L1-004] Verifies Universal Grammar AST decomposition of cryptic clues."""
        clue = GLOBAL_LEXICON.get_clue_for_word(
            word="ORCHESTRA",
            clue_id="clue_01",
            slot_id="slot_01",
            number=1,
            direction=Direction.ACROSS,
        )
        self.assertEqual(clue.answer, "ORCHESTRA")
        self.assertEqual(clue.length, 9)
        self.assertEqual(clue.clue_type, ClueType.ANAGRAM)
        self.assertEqual(clue.definition, "musical arrangement")
        self.assertEqual(clue.indicator, "ordered")
        self.assertEqual(sorted(clue.fodder.lower()), sorted("orchestra"))
        self.assertIn("Anagram", clue.explanation)

    def test_csp_engine_distinct_grid_solving(self):
        """Verifies AC-3 CSP solver generates a mathematically valid grid with distinct answers."""
        engine = CrosswordCspEngine()
        puzzle = engine.generate_puzzle(
            grid_id="test_quick_grid",
            title="Test Quick Grid",
            grid_template=TEMPLATE_7X7_QUICK,
            max_backtracks=4000,
        )

        self.assertEqual(puzzle.size_rows, 7)
        self.assertEqual(puzzle.size_cols, 7)
        self.assertEqual(len(puzzle.slots), 12)

        # Invariant: All assigned words must be distinct
        answers = [s.answer for s in puzzle.slots]
        self.assertEqual(len(answers), len(set(answers)), "Duplicate answers found in crossword grid")

        # Invariant: Intersecting across and down slots must match characters
        intersections = engine.compute_intersections(puzzle.slots)
        slot_map = {s.slot_id: s for s in puzzle.slots}

        for (s1_id, s2_id), (idx1, idx2) in intersections.items():
            s1 = slot_map[s1_id]
            s2 = slot_map[s2_id]
            self.assertEqual(
                s1.answer[idx1],
                s2.answer[idx2],
                f"Intersection mismatch between {s1_id} and {s2_id} at ({idx1}, {idx2})",
            )

    def test_landauer_search_entropy_accounting(self):
        """[L1-008] Verifies Landauer thermodynamic bit erasure tracking during backtracking."""
        engine = CrosswordCspEngine()
        slots = engine.extract_slots(TEMPLATE_7X7_QUICK)
        intersections = engine.compute_intersections(slots)

        solution, audit = engine.solve_grid(slots, intersections, max_backtracks=4000)
        self.assertIsNotNone(solution)
        self.assertGreaterEqual(audit.candidate_domain_erased_bits, 0.0)
        self.assertGreaterEqual(audit.joules_dissipated, 0.0)
        self.assertGreaterEqual(audit.pruned_branches_ratio, 0.0)

    def test_landauer_budget_exceeded_error_enforced(self):
        """[L1-008] Verifies that exhausting the Landauer backtrack lease raises LandauerBudgetExceededError."""
        engine = CrosswordCspEngine()
        slots = engine.extract_slots(TEMPLATE_7X7_QUICK)
        intersections = engine.compute_intersections(slots)

        # Force immediate exhaustion with max_backtracks=0
        with self.assertRaises(LandauerBudgetExceededError):
            engine.solve_grid(slots, intersections, max_backtracks=0)

    def test_asynchronous_worker_pool_isolation(self):
        """[L1-015_1] Verifies decoupled background worker execution for CPU-bound CSP synthesis."""
        pool = CrosswordWorkerPool(max_concurrent_workers=1)
        job = pool.enqueue_synthesis_job(grid_size=7)

        self.assertIsNotNone(job.job_id)
        self.assertIn(job.status, [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.COMPLETED])

        # Wait for worker thread to complete
        start_wait = time.time()
        while job.status in [JobStatus.PENDING, JobStatus.RUNNING] and (time.time() - start_wait < 5.0):
            time.sleep(0.05)

        self.assertEqual(job.status, JobStatus.COMPLETED)
        self.assertIsNotNone(job.result_grid)
        self.assertEqual(job.progress_pct, 100.0)

    def test_session_store_optimistic_concurrency_and_deltas(self):
        """[L1-011_3 & L1-002] Verifies partitioned solver sessions and optimistic delta concurrency."""
        import uuid
        sess_id = f"sess_test_{uuid.uuid4().hex[:8]}"
        store = SessionStore()
        session = store.get_or_create_session(sess_id, puzzle_id="puzzle_quick_01")
        self.assertEqual(session.version, 1)

        # Apply valid delta
        updated, success = store.apply_delta(sess_id, row=0, col=0, char="C", expected_version=1)
        self.assertTrue(success)
        self.assertEqual(updated.version, 2)
        self.assertEqual(updated.cells_entered["0,0"], "C")

        # Conflict on stale version
        conflict_session, success_stale = store.apply_delta(
            sess_id, row=0, col=1, char="A", expected_version=1
        )
        self.assertFalse(success_stale)
        self.assertEqual(conflict_session.version, 2)

    def test_demarcated_exception_enclave_containment(self):
        """[L1-016] Verifies Demarcated Exception Enclave blast-radius isolation."""
        with ExceptionEnclave("TEST_CW_ENCLAVE", "crossword_fault_injection") as enclave:
            raise KeyError("Simulated missing grid slot")

        self.assertIsNotNone(enclave.caught)
        self.assertIn("Simulated missing grid slot", enclave.caught)
        self.assertIsNotNone(enclave.witness)
        self.assertTrue(enclave.witness["blast_radius_isolated"])


if __name__ == "__main__":
    unittest.main()
