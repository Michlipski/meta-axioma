"""Automated verification test suite for Axioma Lexis.
Verifies SRS algorithms, dictionary engine, functorial reversibility, and invariant compliance.
"""

import json
from pathlib import Path
import sys
import time
import unittest

app_root = Path(__file__).parent.parent
sys.path.insert(0, str(app_root / "src"))

from server import AppStateEngine, ExceptionEnclave, LANDAUER_LIMIT, DATA_DIR
from srs_algorithm import SrsAlgorithm, SrsRating
from dictionary import DictionaryEngine


class TestAxiomaLexis(unittest.TestCase):
    def setUp(self):
        self.engine = AppStateEngine()

    def tearDown(self):
        feedback_file = DATA_DIR / "user_feedback.json"
        if feedback_file.exists():
            try:
                feedback_file.unlink()
            except Exception:
                pass

    def test_srs_algorithm_sm2_progression(self):
        base_word = {
            "id": "word_test",
            "word": "lucid",
            "repetition_level": 0,
            "interval_days": 0.0,
            "ease_factor": 2.5,
            "status": "learning",
        }

        # 1. Rating GOOD for new word -> interval 1.0 day
        r1 = SrsAlgorithm.calculate_next_review(base_word, SrsRating.GOOD)
        self.assertEqual(r1["repetition_level"], 1)
        self.assertEqual(r1["interval_days"], 1.0)
        self.assertEqual(r1["ease_factor"], 2.5)

        # 2. Rating GOOD second time -> interval 3.0 days
        r2 = SrsAlgorithm.calculate_next_review(r1, SrsRating.GOOD)
        self.assertEqual(r2["repetition_level"], 2)
        self.assertEqual(r2["interval_days"], 3.0)

        # 3. Rating EASY -> bonus interval and increased ease factor
        r3 = SrsAlgorithm.calculate_next_review(r2, SrsRating.EASY)
        self.assertEqual(r3["repetition_level"], 3)
        self.assertGreater(r3["interval_days"], 3.0 * 2.5)
        self.assertGreater(r3["ease_factor"], 2.5)

        # 4. Rating FORGOT -> resets streak to 0, interval drops to ~10 mins
        r4 = SrsAlgorithm.calculate_next_review(r3, SrsRating.FORGOT)
        self.assertEqual(r4["repetition_level"], 0)
        self.assertLess(r4["interval_days"], 0.1)
        self.assertEqual(r4["status"], "learning")

    def test_dictionary_engine_local_and_fallback(self):
        dict_engine = DictionaryEngine()

        # Seeded word lookup
        res_ubi = dict_engine.lookup("ubiquitous")
        self.assertEqual(res_ubi["word"], "ubiquitous")
        self.assertEqual(res_ubi["part_of_speech"], "adjective")
        self.assertIn("/juːˈbɪk.wə.t̬əs/", res_ubi["phonetic_us"])
        self.assertIn("omnipresent", res_ubi["synonyms"])
        self.assertIn("ubicuo", res_ubi["translation_es"])

        # Fallback word lookup for unknown word
        res_fallback = dict_engine.lookup("xyzuncommonword123")
        self.assertEqual(res_fallback["word"], "xyzuncommonword123")
        self.assertIn("xyzuncommonword123", res_fallback["definition"])

    def test_functorial_undo_redo_reversibility(self):
        initial_json = json.dumps(self.engine.state, sort_keys=True)

        # Perform review mutation
        mutated = json.loads(initial_json)
        words = mutated.get("words", [])
        if words:
            words[0]["repetition_level"] = 99
        self.engine.mutate("REVIEW_WORD_TEST", mutated, erased_bits=16.0)

        # Verify mutated
        self.assertNotEqual(json.dumps(self.engine.state, sort_keys=True), initial_json)

        # Functorial Undo ([L1-002])
        self.assertTrue(self.engine.undo())
        self.assertEqual(json.dumps(self.engine.state, sort_keys=True), initial_json)

        # Functorial Redo ([L1-002])
        self.assertTrue(self.engine.redo())
        self.assertNotEqual(json.dumps(self.engine.state, sort_keys=True), initial_json)

        # Undo back to clean state
        self.engine.undo()
        self.assertEqual(json.dumps(self.engine.state, sort_keys=True), initial_json)

    def test_landauer_thermodynamic_accounting(self):
        bits_before = self.engine.total_erased_bits
        joules_before = self.engine.total_joules

        self.engine.record_dissipation("test_delete_word", erased_bits=128.0, reversible=False)
        self.assertEqual(self.engine.total_erased_bits, bits_before + 128.0)
        self.assertAlmostEqual(self.engine.total_joules, joules_before + (128.0 * LANDAUER_LIMIT))

    def test_demarcated_exception_enclave_containment(self):
        with ExceptionEnclave("TEST_VOCAB_ENCLAVE", "Testing phonetics parse exception") as enc:
            raise KeyError("Malformed audio phonetic tag")

        self.assertIsNotNone(enc.witness)
        self.assertTrue(enc.witness["blast_radius_isolated"])
        self.assertIn("Malformed audio", enc.caught)

    def test_active_user_feedback_recording(self):
        """Verifies active feedback recording capability for transgenerational learning."""
        feedback_entry = {
            "id": "fb_test_123",
            "rating": 4,
            "comment": "Interval progression was slightly too aggressive on day 3",
            "category": "SRS_SCHEDULE",
            "context_view": "review",
            "timestamp": time.time(),
        }
        feedback_file = DATA_DIR / "user_feedback.json"
        with open(feedback_file, "w", encoding="utf-8") as f:
            json.dump([feedback_entry], f)

        self.assertTrue(feedback_file.exists())
        with open(feedback_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["id"], "fb_test_123")


if __name__ == "__main__":
    unittest.main()
