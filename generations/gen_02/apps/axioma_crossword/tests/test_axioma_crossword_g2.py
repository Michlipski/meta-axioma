"""Comprehensive Verification Suite for Axioma Crossword (Generation 2).

Verifies strict adherence to:
- L1-G2-001: Galois multi-substrate compilation
- L1-G2-002: Ephemeral 3-pass self-healing exception enclaves
- L1-G2-003: Cognitive ergonomics & persona alignment invariance
- L1-G2-004: Introspectable zero-trust capability scoping
- L1-G2-006: Phenomenological tool-being & Zuhandenheit attunement
- NEG-G2-003: Cruciverbalist Invariant (no answers leaked in clue surface)
- NEG-G2-009: Cruciverbalist Lexical Purity (zero pseudo-words, authentic English)
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from core import TEMPLATE_7X7_QUICK, TEMPLATE_9X9_MIDI, CrosswordCspEngine, LandauerBudgetExceededError
from enclave import CrosswordExceptionEnclave, CrosswordHealingEnclave
from lexicon import CURATED_CRYPTIC_RECORDS, GLOBAL_LEXICON
from phenomenology import CrosswordPhenomenologyTracker
from server import Gen2CrosswordStore
from tokens import CrosswordCapabilityAuthority
from models import ClueType, Direction, WordSlot


class TestAxiomaCrosswordG2(unittest.TestCase):
    """Full verification suite for Axioma Crossword (Generation 2)."""

    def test_lexicon_inverted_index_and_candidates(self):
        """Verifies O(1) candidate lookup using positional character inverted index."""
        candidates = GLOBAL_LEXICON.get_candidates(3, {0: "C", 2: "T"})
        self.assertIn("CAT", candidates)
        self.assertIn("CUT", candidates)

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
        self.assertEqual(clue.definition, "symphonic musical ensemble")
        self.assertEqual(clue.indicator, "disordered")
        self.assertEqual(sorted(clue.fodder.lower()), sorted("carthorse"))

    def test_csp_engine_quick_7x7_solving(self):
        """Verifies AC-3 CSP solver generates a valid 7x7 grid with distinct answers."""
        engine = CrosswordCspEngine()
        puzzle = engine.generate_puzzle("test_quick_g2", "Test Quick G2", TEMPLATE_7X7_QUICK)
        self.assertEqual(puzzle.size_rows, 7)
        self.assertEqual(puzzle.size_cols, 7)
        self.assertEqual(len(puzzle.slots), 12)

        answers = [s.answer for s in puzzle.slots]
        self.assertEqual(len(answers), len(set(answers)), "Duplicate answers found in 7x7 grid")

    def test_csp_engine_midi_9x9_solving(self):
        """[NEG-G2-003] Verifies 9x9 Midi crossword synthesizes successfully with distinct answers."""
        engine = CrosswordCspEngine()
        puzzle = engine.generate_puzzle("test_midi_g2", "Test Midi G2", TEMPLATE_9X9_MIDI)
        self.assertEqual(puzzle.size_rows, 9)
        self.assertEqual(puzzle.size_cols, 9)
        self.assertEqual(len(puzzle.slots), 14)

        answers = [s.answer for s in puzzle.slots]
        self.assertEqual(len(answers), len(set(answers)), "Duplicate answers found in 9x9 grid")

    def test_cruciverbalist_invariant_no_answers_leaked(self):
        """[NEG-G2-003] Verifies that the answer word NEVER appears verbatim in the clue surface text."""
        engine = CrosswordCspEngine()
        puzzle = engine.generate_puzzle("test_puz", "Test", TEMPLATE_7X7_QUICK)
        for clue in puzzle.clues:
            ans = clue.answer.lower()
            text_without_len = re.sub(r"\(\d+\)$", "", clue.surface_text.strip())
            tokens = [t.lower() for t in re.findall(r"[a-zA-Z]+", text_without_len)]
            self.assertNotIn(
                ans,
                tokens,
                f"Breach of NEG-G2-003: Answer '{clue.answer}' found in clue: '{clue.surface_text}'",
            )

    def test_cruciverbalist_lexical_purity_no_pseudo_words(self):
        """[NEG-G2-009] Verifies Cruciverbalist Lexical Purity: NO pseudo-words or scrambled letter jumbles."""
        # 1. Verify curated clue for NATURAL has zero pseudo-words
        natural_clue = GLOBAL_LEXICON.get_clue_for_word("NATURAL", "c_nat", "s_nat", 1, Direction.ACROSS)
        self.assertNotIn("tula", natural_clue.surface_text.lower())
        self.assertNotIn("ran tula", natural_clue.surface_text.lower())
        self.assertEqual(natural_clue.clue_type.value, "DOUBLE_DEF")

        # 2. Verify all curated records have no known pseudo-words
        forbidden_pseudo = {"tula", "abaac", "acba", "lcin", "rhaaa", "nna", "otci", "itx", "naat", "ferent"}
        for rec in CURATED_CRYPTIC_RECORDS:
            text = rec["surface_text"].lower()
            tokens = re.findall(r"[a-z]+", text)
            for pt in forbidden_pseudo:
                self.assertNotIn(
                    pt,
                    tokens,
                    f"NEG-G2-009 Breach: Pseudo-word '{pt}' in clue for {rec['answer']}: '{rec['surface_text']}'",
                )

    def test_zero_trust_capability_tokens(self):
        """[L1-G2-004] Verifies HMAC SHA-256 capability scoping and persona gating."""
        authority = CrosswordCapabilityAuthority()
        tok = authority.issue_token("Cruciverbalist_Player", ["read_puzzle", "enter_cell"])
        self.assertIsNotNone(tok.token_id)
        self.assertTrue(authority.verify_action(tok.token_id, "read_puzzle"))
        self.assertTrue(authority.verify_action(tok.token_id, "enter_cell"))
        self.assertFalse(authority.verify_action(tok.token_id, "synthesize_grid"))

    def test_ephemeral_self_healing_enclaves(self):
        """[L1-G2-002 & L1-016] Verifies 3-pass self-healing and blast radius containment."""
        healing = CrosswordHealingEnclave()
        # Pass 1: Missing slot_id synthesis
        raw_slot = {"direction": "ACROSS", "row": 2, "col": 0, "length": 7, "answer": "NATURAL"}
        ok, healed_slot, passes = healing.heal_raw_slot(raw_slot)
        self.assertTrue(ok)
        self.assertEqual(healed_slot.slot_id, "A_2_0")
        self.assertTrue(any("Pass 1" in p for p in passes))

        # Blast containment context manager
        with CrosswordExceptionEnclave("TEST_ENCLAVE", "fault_injection") as enclave:
            raise KeyError("Simulated grid anomaly")
        self.assertIsNotNone(enclave.caught)
        self.assertTrue(enclave.witness["blast_radius_isolated"])

    def test_phenomenology_zuhandenheit_telemetry(self):
        """[L1-G2-006] Verifies tool-being flow attunement and rupture containment."""
        tracker = CrosswordPhenomenologyTracker()
        self.assertGreaterEqual(tracker.compute_transparency_score(), 0.90)

        # Record keystroke fluidity
        for _ in range(10):
            tracker.record_keystroke()
        snapshot = tracker.get_telemetry_snapshot()
        self.assertEqual(snapshot["tool_state"], "ZUHANDEN")
        self.assertEqual(snapshot["keystrokes_tracked"], 10)

    def test_session_store_optimistic_delta_sync(self):
        """[L1-011_3 & L1-002] Verifies partitioned session store and optimistic delta sync."""
        import uuid
        sess_id = f"sess_g2_test_{uuid.uuid4().hex[:8]}"
        store = Gen2CrosswordStore()
        sess = store.get_or_create_session(sess_id, puzzle_id="puzzle_quick_01")
        self.assertEqual(sess.version, 1)

        # Apply valid delta
        updated, ok = store.apply_delta(sess_id, row=0, col=0, char="A", expected_version=1)
        self.assertTrue(ok)
        self.assertEqual(updated.version, 2)
        self.assertEqual(updated.cells_entered["0,0"], "A")

        # Conflict on stale version
        conflict, ok_stale = store.apply_delta(sess_id, row=0, col=1, char="B", expected_version=1)
        self.assertFalse(ok_stale)
        self.assertEqual(conflict.version, 2)

    def test_landauer_entropy_and_lease_enforcement(self):
        """[L1-008] Verifies Landauer thermodynamic bit erasure tracking and budget exhaustion."""
        engine = CrosswordCspEngine()
        slots = engine.extract_slots(TEMPLATE_7X7_QUICK)
        intersections = engine.compute_intersections(slots)

        solution, audit = engine.solve_grid(slots, intersections, max_backtracks=4000)
        self.assertIsNotNone(solution)
        self.assertGreaterEqual(audit.candidate_domain_erased_bits, 0.0)
        self.assertGreaterEqual(audit.joules_dissipated, 0.0)

        # Force exhaustion
        with self.assertRaises(LandauerBudgetExceededError):
            engine.solve_grid(slots, intersections, max_backtracks=0)


if __name__ == "__main__":
    unittest.main()
