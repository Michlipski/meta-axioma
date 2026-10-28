"""
Unit tests validating HTTP routing, API endpoints, feedback persistence,
and AsyncIO streams for the Axioma Evolution Dashboard Server.
"""

import asyncio
import json
import unittest
from pathlib import Path
import sys

APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from src.data_store import EvolutionDataStore
from server import process_http_request, handle_async_http_client


class TestAxiomaEvolutionDashboardRuntime(unittest.TestCase):
    def setUp(self):
        self.store = EvolutionDataStore()

    def test_01_static_index_and_dashboard(self):
        status, headers, body = process_http_request("GET", "/", {}, b"", self.store)
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn(b"Meta-Axioma", body)

        status, headers, body = process_http_request("GET", "/dashboard", {}, b"", self.store)
        self.assertEqual(status, 200)

    def test_02_health_endpoint(self):
        status, headers, body = process_http_request("GET", "/api/health", {}, b"", self.store)
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["stages_count"], 8)
        self.assertEqual(data["transformations_count"], 7)
        self.assertEqual(data["subsystems_count"], 6)

    def test_03_philosophy_endpoint(self):
        status, headers, body = process_http_request("GET", "/api/philosophy", {}, b"", self.store)
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertIn("surface_layman", data)
        sl = data["surface_layman"]
        self.assertIn("row_1_pillars", sl)
        self.assertIn("row_2_pillars", sl)
        self.assertEqual(len(sl["row_1_pillars"]), 3)
        self.assertEqual(len(sl["row_2_pillars"]), 3)
        self.assertIn("core_pillars", sl)
        self.assertEqual(len(sl["core_pillars"]), 6)

        # Verify the older two core pillars are kept, jettison is removed, and all 4 new pillars exist
        pillar_ids = [p["id"] for p in sl["core_pillars"]]
        self.assertIn("bounding_in_math", pillar_ids)
        self.assertIn("brain_vs_muscle", pillar_ids)
        self.assertIn("dual_lattice_projection", pillar_ids)
        self.assertIn("sovereign_separation_of_powers", pillar_ids)
        self.assertIn("thermodynamic_entropy_recycling", pillar_ids)
        self.assertIn("functorial_dialectic", pillar_ids)
        self.assertNotIn("jettison", " ".join(pillar_ids))

    def test_04_g4b_architecture_endpoint(self):
        status, headers, body = process_http_request("GET", "/api/g4b", {}, b"", self.store)
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertEqual(len(data.get("services", [])), 5)

    def test_05_simulations_endpoint(self):
        status, headers, body = process_http_request("GET", "/api/simulations", {}, b"", self.store)
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertIn("simulations", data)

        status, headers, body = process_http_request("GET", "/api/simulations/axioma_go", {}, b"", self.store)
        self.assertEqual(status, 200)
        sim = json.loads(body.decode("utf-8"))
        self.assertEqual(sim["total_steps"], 5)

    def test_06_diff_endpoint(self):
        status, headers, body = process_http_request("GET", "/api/diff?a=s0&b=g4b", {}, b"", self.store)
        self.assertEqual(status, 200)
        diff = json.loads(body.decode("utf-8"))
        self.assertEqual(diff["stage_a"]["id"], "s0")
        self.assertEqual(diff["stage_b"]["id"], "g4b")
        self.assertIn("nodes_delta", diff)

    def test_07_feedback_lifecycle(self):
        test_payload = {
            "author": "Test Recruiter",
            "rating": 5,
            "comment": "Outstanding clarity and mathematical depth.",
        }
        status, headers, body = process_http_request(
            "POST",
            "/api/feedback",
            {"Content-Type": "application/json"},
            json.dumps(test_payload).encode("utf-8"),
            self.store,
        )
        self.assertEqual(status, 201)
        resp = json.loads(body.decode("utf-8"))
        self.assertEqual(resp["status"], "created")

        status, headers, body = process_http_request("GET", "/api/feedback", {}, b"", self.store)
        self.assertEqual(status, 200)
        items = json.loads(body.decode("utf-8"))
        self.assertTrue(len(items) >= 1)

    def test_08_asyncio_client_stream(self):
        async def run_async_test():
            req_data = b"GET /api/health HTTP/1.1\r\nHost: localhost\r\n\r\n"
            reader = asyncio.StreamReader()
            reader.feed_data(req_data)
            reader.feed_eof()

            class DummyWriter:
                def __init__(self):
                    self.data = bytearray()
                    self.closed = False

                def write(self, b):
                    self.data.extend(b)

                async def drain(self):
                    pass

                def close(self):
                    self.closed = True

                async def wait_closed(self):
                    pass

            writer = DummyWriter()
            await handle_async_http_client(reader, writer, self.store)
            self.assertIn(b"200 OK", bytes(writer.data))
            self.assertIn(b'"status": "healthy"', bytes(writer.data))

        asyncio.run(run_async_test())


if __name__ == "__main__":
    unittest.main()
