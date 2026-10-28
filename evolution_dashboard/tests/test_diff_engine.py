"""
Unit tests validating the Generational Diff Engine and Cross-Schema Invariant Reconciliation.
Enforces invariant preservation and schema normalization across all 8 generations (S0 -> G4b).
"""

from __future__ import annotations

import unittest
from pathlib import Path
import sys

APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from src.data_store import EvolutionDataStore, parse_invariant


class TestGenerationalDiffEngine(unittest.TestCase):
    def setUp(self):
        self.store = EvolutionDataStore()

    def test_01_parse_invariant_dictionary_schemas(self):
        # Full dict schema
        inv1 = {
            "id": "L1-G3B-000",
            "name": "Waterloo Tier 1 Situation of Concern Normalization",
            "desc": "Solution-agnostic extraction of Macro/Meso/Micro frictions",
            "status": "ACTIVE_STRUCTURAL",
        }
        res1 = parse_invariant(inv1)
        self.assertEqual(res1["id"], "L1-G3B-000")
        self.assertEqual(res1["name"], "Waterloo Tier 1 Situation of Concern Normalization")
        self.assertEqual(res1["status"], "ACTIVE_STRUCTURAL")
        self.assertIn("L1-G3B-000 (Waterloo Tier 1 Situation of Concern Normalization)", res1["label"])

        # Dict with code and title
        inv2 = {"code": "AX-MEM-001", "title": "Memory Boundedness"}
        res2 = parse_invariant(inv2)
        self.assertEqual(res2["id"], "AX-MEM-001")
        self.assertEqual(res2["name"], "Memory Boundedness")

    def test_02_parse_invariant_string_schemas(self):
        # Format 1: ID (Name) - G4b standard format
        res1 = parse_invariant("L1-G3B-000 (Waterloo Situation of Concern Hierarchy)")
        self.assertEqual(res1["id"], "L1-G3B-000")
        self.assertEqual(res1["name"], "Waterloo Situation of Concern Hierarchy")

        # Format 2: [ID] (Name) or [ID]: Name
        res2 = parse_invariant("[L1-G4B-001] Sovereign Decoupled Research Boundary")
        self.assertEqual(res2["id"], "L1-G4B-001")
        self.assertEqual(res2["name"], "Sovereign Decoupled Research Boundary")

        # Format 3: ID: Name
        res3 = parse_invariant("L1-G4B-004: Asymmetric RFC Protocol Bus")
        self.assertEqual(res3["id"], "L1-G4B-004")
        self.assertEqual(res3["name"], "Asymmetric RFC Protocol Bus")

        # Format 4: ID - Name
        res4 = parse_invariant("NEG-G1B-001 - Anti-Phantom Emission Gate")
        self.assertEqual(res4["id"], "NEG-G1B-001")
        self.assertEqual(res4["name"], "Anti-Phantom Emission Gate")

        # Format 5: Standalone ID
        res5 = parse_invariant("L1-002")
        self.assertEqual(res5["id"], "L1-002")
        self.assertEqual(res5["name"], "L1-002")

    def test_03_g3b_to_g4b_cross_schema_diff(self):
        diff = self.store.get_generational_diff("g3b", "g4b")
        self.assertNotIn("error", diff)

        # 6 invariants retained from G3b into G4b
        expected_retained = [
            "L1-G3B-000",
            "L1-G3B-011",
            "L1-G3B-012",
            "L1-G3B-014",
            "L1-G3B-017",
            "L1-G3B-018",
        ]
        retained = diff["invariants_retained"]
        for inv in expected_retained:
            self.assertIn(inv, retained, f"Expected {inv} to be retained in G4b")
        self.assertEqual(len(retained), 6)

        # 6 invariants added / restored in G4b
        expected_added = [
            "L1-002",
            "L1-G4B-001",
            "L1-G4B-002",
            "L1-G4B-003",
            "L1-G4B-004",
            "NEG-G1B-001",
        ]
        added = diff["invariants_added"]
        for inv in expected_added:
            self.assertIn(inv, added, f"Expected {inv} to be added in G4b")
        self.assertEqual(len(added), 6)

        # 3 invariants retired from G3b
        expected_retired = ["L1-G3B-013", "L1-G3B-015", "L1-G3B-016"]
        retired = diff["invariants_retired"]
        for inv in expected_retired:
            self.assertIn(inv, retired, f"Expected {inv} to be retired from G3b")
        self.assertEqual(len(retired), 3)

        # Invariant details verification
        self.assertEqual(len(diff["invariants_details"]["added"]), 6)
        self.assertEqual(len(diff["invariants_details"]["retained"]), 6)
        self.assertEqual(len(diff["invariants_details"]["retired"]), 3)

    def test_04_s0_to_g1_low_level_jettison_diff(self):
        diff = self.store.get_generational_diff("s0", "g1")
        self.assertNotIn("error", diff)

        # Scaffolding axioms L0-001..003 retired at Low-Level Jettison
        self.assertIn("L0-001", diff["invariants_retired"])
        self.assertIn("L0-002", diff["invariants_retired"])
        self.assertIn("L0-003", diff["invariants_retired"])

        # Structural axioms retained
        self.assertIn("L1-002", diff["invariants_retained"])
        self.assertIn("L1-008", diff["invariants_retained"])
        self.assertIn("L1-015", diff["invariants_retained"])

        # New search heuristics added
        self.assertIn("L1-017", diff["invariants_added"])
        self.assertIn("L1-018", diff["invariants_added"])

    def test_05_identity_diff(self):
        for stage_id in ["s0", "g1", "g2", "g3", "g1b", "g2b", "g3b", "g4b"]:
            diff = self.store.get_generational_diff(stage_id, stage_id)
            self.assertEqual(diff["invariants_added"], [], f"Stage {stage_id} identity diff should have 0 added")
            self.assertEqual(diff["invariants_retired"], [], f"Stage {stage_id} identity diff should have 0 retired")
            self.assertEqual(diff["nodes_delta"], 0, f"Stage {stage_id} identity diff should have 0 nodes_delta")
            self.assertEqual(diff["invariants_delta"], 0, f"Stage {stage_id} identity diff should have 0 invariants_delta")

    def test_06_exhaustive_pairwise_diff_matrix(self):
        all_stages = [s["id"] for s in self.store.get_stages()]
        self.assertEqual(len(all_stages), 8)
        # Verify all 64 pairs
        for a in all_stages:
            for b in all_stages:
                diff = self.store.get_generational_diff(a, b)
                self.assertIn("stage_a", diff)
                self.assertIn("stage_b", diff)
                self.assertEqual(diff["stage_a"]["id"], a)
                self.assertEqual(diff["stage_b"]["id"], b)
                self.assertIn("invariants_added", diff)
                self.assertIn("invariants_retained", diff)
                self.assertIn("invariants_retired", diff)
                self.assertIn("nodes_delta", diff)
                self.assertIn("evolutionary_leap", diff)


if __name__ == "__main__":
    unittest.main()
