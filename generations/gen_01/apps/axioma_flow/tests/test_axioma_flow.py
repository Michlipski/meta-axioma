"""Unit test suite for compiled production app 'Axioma Flow'."""

import json
from pathlib import Path
import sys
import unittest

# Import server components from compiled app
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from server import AppStateEngine, ExceptionEnclave, LANDAUER_LIMIT


class TestAxiomaFlowApp(unittest.TestCase):
    def setUp(self):
        self.engine = AppStateEngine()

    def test_initial_state_loaded(self):
        self.assertIn("tasks", self.engine.state)
        tasks = self.engine.state["tasks"]
        self.assertGreaterEqual(len(tasks), 4)

    def test_create_and_move_task(self):
        initial_count = len(self.engine.state["tasks"])
        new_task = {
            "id": "task_custom_1",
            "title": "Test Custom Invariant",
            "status": "backlog",
            "priority": "high",
        }
        new_state = dict(self.engine.state)
        new_state["tasks"] = list(self.engine.state["tasks"]) + [new_task]
        self.engine.mutate("CREATE_TASK", new_state, erased_bits=64.0)

        self.assertEqual(len(self.engine.state["tasks"]), initial_count + 1)
        self.assertEqual(len(self.engine.history), 1)
        self.assertGreater(self.engine.total_erased_bits, 0.0)

        # Move task to in_progress
        updated_state = dict(self.engine.state)
        updated_tasks = []
        for t in updated_state["tasks"]:
            if t["id"] == "task_custom_1":
                copy_t = dict(t)
                copy_t["status"] = "in_progress"
                updated_tasks.append(copy_t)
            else:
                updated_tasks.append(t)
        updated_state["tasks"] = updated_tasks
        self.engine.mutate("MOVE_TASK", updated_state, erased_bits=16.0)

        # Verify moved
        target = next(t for t in self.engine.state["tasks"] if t["id"] == "task_custom_1")
        self.assertEqual(target["status"], "in_progress")

    def test_functorial_undo_redo_reversibility(self):
        initial_snapshot = json.dumps(self.engine.state, sort_keys=True)

        # Apply mutation
        mutated_state = dict(self.engine.state)
        mutated_state["tasks"] = [t for t in self.engine.state["tasks"] if t["id"] != "task_101"]
        self.engine.mutate("DELETE_TASK", mutated_state, erased_bits=128.0)
        self.assertNotEqual(json.dumps(self.engine.state, sort_keys=True), initial_snapshot)

        # Functorial Undo (L1-002)
        success = self.engine.undo()
        self.assertTrue(success)
        self.assertEqual(json.dumps(self.engine.state, sort_keys=True), initial_snapshot)

        # Functorial Redo (L1-002)
        success = self.engine.redo()
        self.assertTrue(success)
        self.assertNotEqual(json.dumps(self.engine.state, sort_keys=True), initial_snapshot)

        # Undo again to restore
        self.engine.undo()
        self.assertEqual(json.dumps(self.engine.state, sort_keys=True), initial_snapshot)

    def test_landauer_thermodynamic_accounting(self):
        initial_bits = self.engine.total_erased_bits
        initial_joules = self.engine.total_joules

        self.engine.record_dissipation("test_lossy_op", erased_bits=100.0, reversible=False)
        self.assertEqual(self.engine.total_erased_bits, initial_bits + 100.0)
        self.assertAlmostEqual(self.engine.total_joules, initial_joules + 100.0 * LANDAUER_LIMIT)

    def test_exception_enclave_blast_radius_containment(self):
        with ExceptionEnclave("TEST_ENCLAVE", "Testing fault isolation") as enclave:
            raise KeyError("Simulated bad key in task payload")

        self.assertIsNotNone(enclave.witness)
        self.assertTrue(enclave.witness["blast_radius_isolated"])
        self.assertIn("Simulated bad key", enclave.caught)


if __name__ == "__main__":
    unittest.main()
