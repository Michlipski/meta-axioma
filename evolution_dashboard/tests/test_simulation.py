"""
Unit tests validating the interactive sample app compilation visual simulation (axioma_go).
"""

import unittest
from pathlib import Path
import sys

APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from src.data_store import EvolutionDataStore


class TestSimulationEngine(unittest.TestCase):
    def setUp(self):
        self.store = EvolutionDataStore()

    def test_axioma_go_simulation_structure(self):
        sim = self.store.get_simulation("axioma_go")
        self.assertIsNotNone(sim)
        self.assertEqual(sim["total_steps"], 5)
        self.assertEqual(len(sim["steps"]), 5)

        step_phases = [s["phase"] for s in sim["steps"]]
        self.assertIn("Epistemic Research & Specification", step_phases[0])
        self.assertIn("Formal Verification & Protocol Negotiation", step_phases[1])
        self.assertIn("Parallel Code Generation", step_phases[2])
        self.assertIn("Byzantine Chaos Fuzzing & Model Verification", step_phases[3])
        self.assertIn("Merkle-DAG Anchoring & Production Release", step_phases[4])

    def test_simulation_step_details(self):
        sim = self.store.get_simulation("axioma_go")
        for step in sim["steps"]:
            self.assertIn("surface_layman", step)
            self.assertIn("what_happens", step["surface_layman"])
            self.assertIn("why_it_matters", step["surface_layman"])
            self.assertIn("analogy", step["surface_layman"])
            self.assertIn("academic_deep_dive", step)
            self.assertIn("concept", step["academic_deep_dive"])
            self.assertIn("invariant_checked", step["academic_deep_dive"])
            self.assertIn("wire_traffic", step)
            self.assertIn("artifact_preview", step)
            self.assertIn("metrics", step)

    def test_simulation_metrics_progression(self):
        sim = self.store.get_simulation("axioma_go")
        # Step 5 should show cumulative spend <= 593,200 (budget ceiling)
        step5_metrics = sim["steps"][4]["metrics"]
        self.assertLessEqual(step5_metrics["tokens_spent"], 593200)
        self.assertEqual(step5_metrics["invariants_locked"], 18)


if __name__ == "__main__":
    unittest.main()
