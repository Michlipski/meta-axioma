"""
Unit tests validating data integrity across all 8 stages, 7 transformations,
and 6 component lineages of the Axioma Evolution Dashboard.
"""

import unittest
from pathlib import Path
import sys

APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from src.data_store import EvolutionDataStore


class TestEvolutionData(unittest.TestCase):
    def setUp(self):
        self.store = EvolutionDataStore()

    def test_all_eight_stages_present(self):
        stages = self.store.get_stages()
        self.assertEqual(len(stages), 8)
        stage_ids = [s["id"] for s in stages]
        expected_ids = ["s0", "g1", "g2", "g3", "g1b", "g2b", "g3b", "g4b"]
        for expected in expected_ids:
            self.assertIn(expected, stage_ids)

    def test_layman_and_academic_fields_on_all_stages(self):
        for st in self.store.get_stages():
            self.assertIn("layman_summary", st, f"Missing layman_summary in {st['id']}")
            self.assertIn("layman_problem", st, f"Missing layman_problem in {st['id']}")
            self.assertIn("layman_breakthrough", st, f"Missing layman_breakthrough in {st['id']}")
            self.assertIn("academic_theory", st, f"Missing academic_theory in {st['id']}")
            self.assertTrue(len(st["layman_summary"]) > 10)

    def test_seven_transformations(self):
        trans = self.store.get_transformations()
        self.assertEqual(len(trans), 7)
        for t in trans:
            self.assertIn("source_stage_id", t)
            self.assertIn("target_stage_id", t)

    def test_six_subsystem_lineages(self):
        subs = self.store.get_components()
        self.assertEqual(len(subs), 6)

    def test_zenith_architecture_points_to_g4b(self):
        zenith = self.store.get_zenith()
        self.assertEqual(zenith.get("generation_id"), "g4b")
        self.assertIn("Generation 4b", zenith.get("name", ""))

    def test_architect_epistemic_contributions(self):
        """Verify all 8 stages contain human architect epistemic contributions."""
        for st in self.store.get_stages():
            self.assertTrue(
                "architect_epistemic_contributions" in st or "michaels_epistemic_contributions" in st,
                f"Missing epistemic contributions in {st['id']}",
            )

    def test_zero_personal_name_leakage_in_evolution_data(self):
        """Invariant [NEG-PRIVACY-001]: Verify zero occurrences of personal name in evolution dataset."""
        import json
        raw = json.dumps(self.store._data, ensure_ascii=False)
        self.assertNotIn("Michael Lipski", raw, "Personal name 'Michael Lipski' found in evolution dataset")
        self.assertNotIn("Lipski", raw, "Personal name 'Lipski' found in evolution dataset")
        self.assertNotIn(" Michael ", raw, "Personal first name 'Michael' found in evolution dataset text")
        self.assertNotIn('"Michael"', raw, "Personal first name 'Michael' found as JSON value")


if __name__ == "__main__":
    unittest.main()
